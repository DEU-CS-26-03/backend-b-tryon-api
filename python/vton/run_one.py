import os
import sys

os.environ["TRANSFORMERS_VERIFY_SCHEDULED_LOAD"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRUST_REMOTE_CODE"] = "True"

current_dir = os.path.dirname(os.path.abspath(__file__))
catvton_path = os.path.join(current_dir, "CatVTON")
if catvton_path not in sys.path:
    sys.path.insert(0, catvton_path)

import torch
from PIL import Image
from huggingface_hub import snapshot_download

_pipeline = None
_automasker = None
_repo_path = None  # 로컬 경로 캐싱 추가


def _load_models():
    global _pipeline, _automasker, _repo_path

    if _pipeline is not None and _automasker is not None:
        return _pipeline, _automasker

    from model.pipeline import CatVTONPipeline
    from model.cloth_masker import AutoMasker

    device = "cuda" if torch.cuda.is_available() else "cpu"
    # GPU면 float16으로 VRAM 절약, CPU면 float32 유지
    weight_dtype = torch.float16 if device == "cuda" else torch.float32

    print(f"[CatVTON] 모델 로딩 중... device={device}, dtype={weight_dtype}")

    # 1회 다운로드 후 로컬 경로를 재사용
    _repo_path = snapshot_download(repo_id="zhengchong/CatVTON")
    base_ckpt = "runwayml/stable-diffusion-inpainting"

    _automasker = AutoMasker(
        densepose_ckpt=os.path.join(_repo_path, "DensePose"),
        schp_ckpt=os.path.join(_repo_path, "SCHP"),
        device=device,
    )

    _pipeline = CatVTONPipeline(
        base_ckpt=base_ckpt,
        attn_ckpt=_repo_path,        # ✅ Fix 2: Hub ID 대신 로컬 경로 전달
        attn_ckpt_version="mix",
        weight_dtype=weight_dtype,
        device=device,
        skip_safety_check=True,      # ✅ Fix 3: 생성자 파라미터로 NSFW 비활성화
    )

    print("[CatVTON] ✅ 모델 로드 완료")
    return _pipeline, _automasker


def run_catvton(
        human_path: str,
        cloth_path: str,
        output_path: str,
        cloth_type: str = "upper",
        num_inference_steps: int = 50,
        guidance_scale: float = 2.5,
) -> tuple[str, object]:
    pipeline, automasker = _load_models()

    print(f"[CatVTON] 마스크 생성 중... cloth_type={cloth_type}")
    mask_result = automasker(human_path, cloth_type)
    mask = mask_result["mask"]

    print(f"[CatVTON] 추론 시작... steps={num_inference_steps}, guidance={guidance_scale}")
    person_image = Image.open(human_path).convert("RGB")
    cloth_image = Image.open(cloth_path).convert("RGB")

    # ✅ Fix 1: pipeline()은 list[PIL.Image]를 직접 반환
    result: list = pipeline(
        image=person_image,
        condition_image=cloth_image,
        mask=mask,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
    )
    output_img = result[0]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_img.save(output_path)
    print(f"[CatVTON] ✅ 결과 저장 완료: {output_path}")

    return output_path, mask