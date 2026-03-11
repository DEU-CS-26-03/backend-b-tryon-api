# python/app/routers/tryon_router.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse

from app.service.tryon_service import run_tryon

router = APIRouter()

@router.post("/tryon")
async def tryon_endpoint(
    user: UploadFile = File(...),
    cloth: UploadFile = File(...),
):
    """
    1) 이미지 업로드
    2) 전처리 + 외부 VTON API + (TF 후처리)
    3) 결과 이미지를 파일로 반환
    """
    result_path = await run_tryon(user, cloth)
    return FileResponse(result_path, media_type="image/png")
