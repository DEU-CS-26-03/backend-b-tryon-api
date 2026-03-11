# python/tests/test_vton_local.py

from pathlib import Path

# 서비스 레이어/유즈케이스를 import
from app.service.tryon_service import run_tryon  # 예시 함수명
# 또는 vton 래퍼를 직접 import
# from vton.vton import run_vton

BASE_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = BASE_DIR / "workspace"
INPUT_DIR = WORKSPACE / "input"
OUTPUT_DIR = WORKSPACE / "output"

def main():
    user_img = INPUT_DIR / "person.jpg"
    cloth_img = INPUT_DIR / "garment.jpg"

    # 1) 서비스 함수 호출 (FastAPI 없이)
    result_path = run_tryon(str(user_img), str(cloth_img))

    print("Result saved at:", result_path)

if __name__ == "__main__":
    main()
