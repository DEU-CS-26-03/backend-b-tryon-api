# python/tests/test_vton_local.py

from pathlib import Path
from fastapi import APIRouter
from ..schemas import TryonRequest, TryonResponse
from ..service.tryon_service import run_tryon_service
from ..config import BASE_URL
from app.service.tryon_service import run_tryon_paths

router = APIRouter(prefix="/tryon", tags=["tryon"])

BASE_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = BASE_DIR / "workspace"
INPUT_DIR = WORKSPACE / "input"

def main():
    user_img = INPUT_DIR / "person.jpg"
    cloth_img = INPUT_DIR / "garment.jpg"

    result_path = run_tryon_paths(str(user_img), str(cloth_img))
    print("Result saved at:", result_path)

if __name__ == "__main__":
    main()

@router.post("", response_model=TryonResponse)
async def tryon(body: TryonRequest):
    result = run_tryon_service(body)
    result_path = result["result_path"]   # "/results/{job_id}/output.png"
    result_url = f"{BASE_URL}{result_path}"

    return {
        "job_id": result["job_id"],
        "mode": result["mode"],
        "result_url": result_url,
    }
