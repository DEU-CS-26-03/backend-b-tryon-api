# python/vton/vton.py

from pathlib import Path
import uuid

import cv2
import numpy as np
from rembg import remove
from PIL import Image

from ..app.config import RESULTS_DIR, TryonMode, TRYON_MODE, WORKFLOW_JSON_PATH, COMFY_OUTPUT_PATH
from .comfyui.client import run_catvton_and_copy
from .external_vton_api import call_external_vton_api
from ai.quality_model import QualityModel


BASE_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = BASE_DIR / "workspace"
DATA_DIR = BASE_DIR / "DATA_DIR"

INPUT_DIR = WORKSPACE / "input"
OUTPUT_DIR = WORKSPACE / "output"

TARGET_WIDTH = 768
TARGET_HEIGHT = 1024


def _ensure_dirs():
    (DATA_DIR / "results").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "tmp").mkdir(parents=True, exist_ok=True)


def _resize_keep_aspect_cv2(img: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    h, w = img.shape[:2]
    tr = target_w / target_h
    cr = w / h
    if cr > tr:
        new_w = int(h * tr)
        sx = (w - new_w) // 2
        cropped = img[:, sx : sx + new_w]
    else:
        new_h = int(w / tr)
        sy = (h - new_h) // 2
        cropped = img[sy : sy + new_h, :]
    return cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_AREA)


def preprocess_person(person_path: str) -> str:
    _ensure_dirs()
    p = Path(person_path)
    person_id = p.stem

    img = cv2.imread(str(p))
    if img is None:
        raise FileNotFoundError(f"Cannot read person image: {person_path}")

    img = _resize_keep_aspect_cv2(img, TARGET_WIDTH, TARGET_HEIGHT)
    out_path = DATA_DIR / "tmp" / f"{person_id}_person.png"
    cv2.imwrite(str(out_path), img)
    return str(out_path)


def preprocess_cloth(cloth_path: str) -> str:
    _ensure_dirs()
    p = Path(cloth_path)
    cloth_id = p.stem

    pil_img = Image.open(str(p)).convert("RGBA")
    nobg = remove(pil_img)
    nobg_np = cv2.cvtColor(np.array(nobg), cv2.COLOR_RGBA2BGRA)

    nobg_np = _resize_keep_aspect_cv2(nobg_np, TARGET_WIDTH, TARGET_HEIGHT)

    out_path = DATA_DIR / "tmp" / f"{cloth_id}_cloth.png"
    cv2.imwrite(str(out_path), nobg_np)
    return str(out_path)


async def run_vton_external(person_pre_path: str, cloth_pre_path: str) -> str:
    """
    전처리된 이미지 경로를 받아 외부 VTON API를 호출하고,
    결과 이미지를 DATA_DIR/results에 저장.
    """
    _ensure_dirs()

    img_bytes, content_type = await call_external_vton_api(
        person_pre_path,
        cloth_pre_path,
    )

    person_id = Path(person_pre_path).stem
    cloth_id = Path(cloth_pre_path).stem

    suffix = ".png" if "png" in content_type else ".jpg"
    out_path = DATA_DIR / "results" / f"{person_id}_{cloth_id}{suffix}"
    out_path.write_bytes(img_bytes)
    return str(out_path)


async def run_vton_quality_pipeline(person_path: str, cloth_path: str) -> str:
    """
    (선택용) 외부 VTON + 품질 모델을 쓰는 전체 파이프라인.
    지금은 사용하지 않지만, 나중에 고도화용으로 남겨두기.
    """
    person_pre = preprocess_person(person_path)
    cloth_pre = preprocess_cloth(cloth_path)

    result_path = await run_vton_external(person_pre, cloth_pre)
    return result_path
    # 확장 버전:
    # candidate_paths: list[str] = [...]
    # q_model = QualityModel()
    # best_path, score = q_model.select_best(candidate_paths)
    # return best_path


def _new_job_paths(ext: str = "png"):
    job_id = str(uuid.uuid4())
    job_dir = Path(RESULTS_DIR) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    output_path = job_dir / f"output.{ext}"
    return job_id, output_path


def run_tryon_mock(request_dto):
    """
    TRYON_MODE=mock 일 때 사용하는 더미 파이프라인.
    """
    job_id, output_path = _new_job_paths("jpg")
    mock_src = BASE_DIR / "mock" / "mock_result.jpg"
    output_path.write_bytes(mock_src.read_bytes())
    return job_id, f"/results/{job_id}/output.jpg"


def run_tryon_real(request_dto):
    human_path = Path(request_dto.human_local_path or request_dto.human_path)
    cloth_path = Path(request_dto.cloth_local_path or request_dto.cloth_path)

    if not human_path.is_file():
        raise FileNotFoundError(f"human image not found: {human_path}")
    if not cloth_path.is_file():
        raise FileNotFoundError(f"cloth image not found: {cloth_path}")

    job_id, output_path = _new_job_paths("png")
    run_catvton_and_copy(
        workflow_json_path=WORKFLOW_JSON_PATH,
        comfy_output_path=COMFY_OUTPUT_PATH,
        save_path=str(output_path),
    )
    return job_id, f"/results/{job_id}/output.png"


def run_tryon_pipeline(request_dto):
    """
    FastAPI 서비스에서 사용하는 최종 파이프라인 진입점.
    TRYON_MODE 에 따라 mock / real 모드를 분기해서 실행하고,
    job_id, mode, result_path를 반환한다.
    """
    if TRYON_MODE == TryonMode.MOCK:
        job_id, result_path = run_tryon_mock(request_dto)
        mode = "mock"
    else:
        job_id, result_path = run_tryon_real(request_dto)
        mode = "real"

    return {
        "job_id": job_id,
        "mode": mode,
        "result_path": result_path,
    }
