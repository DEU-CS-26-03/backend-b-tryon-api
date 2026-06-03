from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.services.tryon_service import run_tryon
import io

router = APIRouter()

@router.post(
    "",
    response_class=Response,
    responses={200: {"content": {"image/jpeg": {}}}},
)
async def infer(
        person_image: UploadFile = File(..., description="사람 이미지"),
        cloth_image:  UploadFile = File(..., description="의류 이미지"),
):
    if person_image.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식")
    if cloth_image.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식")

    person_bytes = await person_image.read()
    cloth_bytes  = await cloth_image.read()

    try:
        result_bytes = await run_tryon(person_bytes, cloth_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추론 실패: {str(e)}")

    return Response(content=result_bytes, media_type="image/jpeg")