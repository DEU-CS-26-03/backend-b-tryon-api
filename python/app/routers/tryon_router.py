# python/app/routers/tryon_router.py
import os, io
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from app.services import jobs_service
from app.services.jobs_service import JobStatus
from app.services.tryon_service import TryonService
from app.core.config import settings

router = APIRouter(prefix="/tryon", tags=["tryon"])

UPLOAD_DIR = os.path.join(os.path.dirname(settings.RESULTS_DIR), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _run_and_update(job_id: str, person_path: str, cloth_path: str, cloth_type: str):
    jobs_service.update_job(job_id, JobStatus.RUNNING)
    try:
        svc = TryonService.get_instance()
        result_path = svc.run(job_id, person_path, cloth_path, cloth_type)
        result_url = f"/tryon/result/{job_id}/image"
        jobs_service.update_job(job_id, JobStatus.DONE, result_url=result_url)
    except Exception as e:
        jobs_service.update_job(job_id, JobStatus.FAILED, error=str(e))

@router.post("/submit")
async def submit_tryon(
        background_tasks: BackgroundTasks,
        person_image: UploadFile = File(...),
        cloth_image:  UploadFile = File(...),
        cloth_type:   str        = Form("upper"),
):
    job = jobs_service.create_job()
    person_path = os.path.join(UPLOAD_DIR, f"{job.job_id}_person.png")
    cloth_path  = os.path.join(UPLOAD_DIR, f"{job.job_id}_cloth.png")
    for path, upload in [(person_path, person_image), (cloth_path, cloth_image)]:
        with open(path, "wb") as f:
            f.write(await upload.read())
    background_tasks.add_task(_run_and_update, job.job_id, person_path, cloth_path, cloth_type)
    return {"job_id": job.job_id, "status": job.status}

@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = jobs_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id":     job.job_id,
        "status":     job.status,
        "result_url": job.result_url,
        "error":      job.error,
    }

@router.get("/result/{job_id}/image")
def get_result_image(job_id: str):
    """DONE 상태일 때 결과 이미지를 파일 스트리밍으로 반환"""
    job = jobs_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=425, detail=f"아직 완료되지 않음: {job.status}")

    result_path = os.path.join(settings.RESULTS_DIR, f"{job_id}.png")
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="결과 파일 없음")

    return FileResponse(
        path=result_path,
        media_type="image/png",
        filename=f"{job_id}.png"
    )