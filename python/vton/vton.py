import os
import sys

os.environ["TRANSFORMERS_VERIFY_SCHEDULED_LOAD"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRUST_REMOTE_CODE"] = "True"

current_dir = os.path.dirname(os.path.abspath(__file__))
catvton_path = os.path.join(current_dir, "..", "CatVTON")
if catvton_path not in sys.path:
    sys.path.insert(0, catvton_path)

import torch
from PIL import Image
from huggingface_hub import snapshot_download

_pipeline = None
_automasker = None


def _load_models():
    global _pipeline, _automasker

    if _pipeline is not None and _automasker is not None:
        return _pipeline, _automasker

    from model.pipeline import CatVTONPipeline
    from model.cloth_masker import AutoMasker

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[CatVTON] 모델 로딩 중... device={device}")

    repo_path = snapshot_download(repo_id="zhengchong/CatVTON")
    base_ckpt = "runwayml/stable-diffusion-inpainting"
    attn_ckpt = "zhengchong/CatVTON"

    _automasker = AutoMasker(
        densepose_ckpt=os.path.join(repo_path, "DensePose"),
        schp_ckpt=os.path.join(repo_path, "SCHP"),
        device=device,
    )

    _pipeline = CatVTONPipeline(
        base_ckpt=base_ckpt,
        attn_ckpt=attn_ckpt,
        device=device,
    )

    def dummy_checker(*args, **kwargs):
        images = kwargs.get("images", args[0] if args else None)
        num = len(images) if isinstance(images, list) else (images.shape[0] if images is not None else 1)
        return images, [False] * num

    if hasattr(_pipeline, "safety_checker"):
        _pipeline.safety_checker = None
    if hasattr(_pipeline, "run_safety_checker"):
        _pipeline.run_safety_checker = dummy_checker

    print("[CatVTON] 모델 로드 완료")
    return _pipeline, _automasker


def run_catvton(
        human_path: str,
        cloth_path: str,
        output_path: str,
        cloth_type: str = "upper",
        num_inference_steps: int = 50,
        guidance_scale: float = 2.5,
) -> tuple:
    pipeline, automasker = _load_models()

    print(f"[CatVTON] 마스크 생성 중... cloth_type={cloth_type}")
    mask_result = automasker(human_path, cloth_type)
    mask = mask_result["mask"]

    print(f"[CatVTON] 추론 시작... steps={num_inference_steps}, guidance={guidance_scale}")
    person_image = Image.open(human_path).convert("RGB")
    cloth_image = Image.open(cloth_path).convert("RGB")

    result = pipeline(
        image=person_image,
        condition_image=cloth_image,
        mask=mask,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
    )

    output_img = result.images[0] if hasattr(result, "images") else result[0]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_img.save(output_path)
    print(f"[CatVTON] 결과 저장 완료: {output_path}")

    return output_path, mask
