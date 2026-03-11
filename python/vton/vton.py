# python/vton/vton.py

from pathlib import Path
from typing import List

import cv2
import numpy as np
from rembg import remove
from PIL import Image

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
        cropped = img[:, sx:sx + new_w]
    else:
        new_h = int(w / tr)
        sy = (h - new_h) // 2
        cropped = img[sy:sy + new_h, :]
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
    결과 이미지를 DATA_DIR/results에 저장. [web:56][web:97][web:100]
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


async def run_tryon_pipeline(person_path: str, cloth_path: str) -> str:
    """
    전체 파이프라인:
    1) 이미지 전처리
    2) 외부 VTON API 호출
    3) TensorFlow 품질 모델로 후처리/선택 (후보 여러 개일 때) [web:64][web:103]
    """
    person_pre = preprocess_person(person_path)
    cloth_pre = preprocess_cloth(cloth_path)

    # 1안: 단일 결과만 생성하는 API인 경우
    result_path = await run_vton_external(person_pre, cloth_pre)
    return result_path

    # 2안(확장): API에서 여러 결과 후보를 얻는 경우
    # candidate_paths: List[str] = [...]
    # q_model = QualityModel()
    # best_path, score = q_model.select_best(candidate_paths)
    # return best_path
