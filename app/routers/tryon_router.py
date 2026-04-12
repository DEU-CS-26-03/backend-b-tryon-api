#  app/routers/tryon_router.py

from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from ..schemas import TryonRequest, TryonResponse
from ..service.tryon_service import run_tryon_service
from ..config import BASE_URL
from app.service.tryon_service import run_tryon_upload

router = APIRouter(prefix="/tryon", tags=["tryon"])

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
