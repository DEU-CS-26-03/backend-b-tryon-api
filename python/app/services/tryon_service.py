import os
import torch
from PIL import Image

from app.core.config import settings

TRYON_MODE = os.getenv("TRYON_MODE", "mock")


class TryonService:
    _instance = None

    @classmethod
    def get_instance(cls) -> "TryonService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.pipeline = None
        self.automasker = None
        self.mask_processor = None
        self.width = 768
        self.height = 1024

        print(f"[TryonService] TRYON_MODE = {TRYON_MODE}")
        os.makedirs(settings.RESULTS_DIR, exist_ok=True)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        if TRYON_MODE == "real":
            self._load_real_pipeline()
        else:
            print("[TryonService] mock 모드 — 모델 로딩 생략")
            self.device = "cpu"

    def _load_real_pipeline(self):
        from diffusers.image_processor import VaeImageProcessor
        from vton.catvton.model.pipeline import CatVTONPipeline
        from vton.catvton.model.cloth_masker import AutoMasker

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if self.device == "cuda" else torch.float32

        print(f"[TryonService] 실제 추론 모드 — device={self.device}")

        self.pipeline = CatVTONPipeline(
            base_ckpt=settings.BASE_MODEL_PATH,
            attn_ckpt=settings.RESUME_PATH,
            attn_ckpt_version="mix",
            weight_dtype=dtype,
            use_tf32=True,
            device=self.device,
        )
        self.automasker = AutoMasker(
            densepose_ckpt=os.path.join(settings.RESUME_PATH, "DensePose"),
            schp_ckpt=os.path.join(settings.RESUME_PATH, "SCHP"),
            device=self.device,
        )
        self.mask_processor = VaeImageProcessor(
            vae_scale_factor=8,
            do_normalize=False,
            do_binarize=True,
            do_convert_grayscale=True,
        )

    def run(
            self,
            job_id: str,
            person_path: str,
            cloth_path: str,
            cloth_type: str = "upper", # 프론트에서 전달받음
            num_inference_steps: int = 50,
            guidance_scale: float = 2.5,
            seed: int = 42,
    ) -> str:
        result_path = os.path.join(settings.RESULTS_DIR, f"{job_id}.png")

        # 1. 의류 카테고리 매핑 (현실적인 확장)
        # CatVTON은 내부적으로 'upper', 'lower', 'overall'만 인식합니다.
        category_map = {
            "upper": "upper",
            "top": "upper",
            "lower": "lower",
            "bottom": "lower",
            "pants": "lower",
            "skirt": "lower",   # 스커트 추가
            "overall": "overall",
            "dress": "overall", # 원피스 추가
            "onepiece": "overall"
        }
        target_type = category_map.get(cloth_type.lower(), "upper")

        if TRYON_MODE != "real":
            dummy = Image.new("RGB", (self.width, self.height), color=(200, 200, 200))
            dummy.save(result_path)
            return result_path

        from vton.catvton.utils import resize_and_crop, resize_and_padding

        person_img = resize_and_crop(Image.open(person_path).convert("RGB"), (self.width, self.height))
        cloth_img = resize_and_padding(Image.open(cloth_path).convert("RGB"), (self.width, self.height))

        # 2. 매핑된 target_type을 automasker에 전달
        mask = self.automasker(person_img, target_type)["mask"]

        # 원피스/드레스일 경우 마스크 경계를 더 부드럽게 (퀄리티 향상)
        blur_radius = 11 if target_type == "overall" else 9
        mask = self.mask_processor.blur(mask, blur_factor=blur_radius)

        generator = torch.Generator(device=self.device).manual_seed(seed)

        result: Image.Image = self.pipeline(
            image=person_img,
            condition_image=cloth_img,
            mask=mask,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator,
        )[0]

        result.save(result_path)
        return result_path