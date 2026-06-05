import io
import os
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

# 경로 주입
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
_VTON_DIR = os.path.join(_PROJECT_ROOT, "vton")

if _VTON_DIR not in sys.path:
    sys.path.insert(0, _VTON_DIR)

import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse
from huggingface_hub import snapshot_download
from PIL import Image

# ── 환경변수 ──────────────────────────────────────────────
BASE_MODEL    = os.getenv("BASE_MODEL_PATH", "booksforcharlie/stable-diffusion-inpainting")
ATTN_CKPT     = os.getenv("ATTN_CKPT_PATH", "zhengchong/CatVTON")
DEVICE        = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
MIXED_PREC    = os.getenv("MIXED_PRECISION", "bf16")
TRYON_MODE    = os.getenv("TRYON_MODE", "real")
# ★ 캡스톤 로컬 노트북 시연 최적화 사이즈
WIDTH, HEIGHT = 512, 768

pipeline = None
automasker = None
mask_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, automasker, mask_processor
    print(f"[startup] TRYON_MODE={TRYON_MODE}, device={DEVICE}")

    if TRYON_MODE != "real":
        yield
        return

    from catvton.model.cloth_masker import AutoMasker
    from catvton.model.pipeline import CatVTONPipeline
    from catvton.utils import init_weight_dtype
    from diffusers.image_processor import VaeImageProcessor

    repo_path = snapshot_download(repo_id=ATTN_CKPT)
    weight_dtype = init_weight_dtype(MIXED_PREC)

    pipeline = CatVTONPipeline(
        base_ckpt=BASE_MODEL,
        attn_ckpt=repo_path,
        attn_ckpt_version="mix",
        weight_dtype=weight_dtype,
        use_tf32=True,
        device=DEVICE,
    )
    mask_processor = VaeImageProcessor(
        vae_scale_factor=8,
        do_normalize=False,
        do_binarize=True,
        do_convert_grayscale=True,
    )
    automasker = AutoMasker(
        densepose_ckpt=os.path.join(repo_path, "DensePose"),
        schp_ckpt=os.path.join(repo_path, "SCHP"),
        device=DEVICE,
    )
    yield

app = FastAPI(title="CatVTON API", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/infer")
async def infer(
        person_image: UploadFile = File(...),
        cloth_image: UploadFile = File(...),
        cloth_type: str = Form("upper"),
        num_inference_steps: int = Form(50),
        guidance_scale: float = Form(2.5),
        seed: int = Form(42)
):
    # ★ 방어 1: 추론 시작 전 이전 찌꺼기 메모리 강제 반환 (OOM 방지)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    try:
        person_bytes = await person_image.read()
        cloth_bytes = await cloth_image.read()

        person_img = Image.open(io.BytesIO(person_bytes)).convert("RGB")
        garment_img = Image.open(io.BytesIO(cloth_bytes)).convert("RGB")

        if TRYON_MODE != "real":
            dummy = Image.new("RGB", (WIDTH, HEIGHT), color=(200, 200, 200))
            buf = io.BytesIO()
            dummy.save(buf, format="JPEG", quality=90)
            return Response(content=buf.getvalue(), media_type="image/jpeg")

        if pipeline is None or automasker is None:
            raise HTTPException(status_code=503, detail="모델 로딩 대기중")

        from catvton.utils import resize_and_crop, resize_and_padding

        person_img = resize_and_crop(person_img, (WIDTH, HEIGHT))
        garment_img = resize_and_padding(garment_img, (WIDTH, HEIGHT))

        category_map = {
            "upper": "upper",
            "top": "upper",
            "lower": "lower",
            "bottom": "lower",
            "pants": "lower",
            "skirt": "lower",
            "overall": "overall",
            "dress": "overall"
        }
        target_type = category_map.get(cloth_type.lower(), "upper")
        print(f"[Inference] 원본 타입: {cloth_type} -> 매핑된 타겟: {target_type}")

        mask = automasker(person_img, target_type)["mask"]

        from PIL import ImageFilter
        mask = mask.filter(ImageFilter.GaussianBlur(radius=9))

        generator = torch.Generator(device=DEVICE).manual_seed(seed)
        result_image = pipeline(
            image=person_img,
            condition_image=garment_img,
            mask=mask,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator,
        )[0]

        buf = io.BytesIO()
        result_image.save(buf, format="JPEG", quality=90)

        print(f"[Inference] {target_type} 추론 완료! Spring으로 이미지 전송.")

        # ★ 방어 2: 정상 완료 직후 즉시 메모리 반환
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return Response(content=buf.getvalue(), media_type="image/jpeg")

    except Exception as e:
        # ★ 방어 3: 에러 시에도 메모리를 쥐고 뻗지 않도록 강제 반환
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e), "message": "GPU 메모리 부족 또는 추론 오류"})