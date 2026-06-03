# python/app/routers/jobs_router.py
import os
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form

from app.services.jobs_service import create_job, get_job, update_job, JobStatus
from app.services.tryon_service import TryonService
from app.core.config import settings

router = APIRouter(prefix="/jobs", tags=["jobs"])

UPLOAD_DIR = os.path.join(os.path.dirname(settings.RESULTS_DIR), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── 백그라운드 추론 함수 ──────────────────────────────
def _run_tryon_background(
        job_id: str,
        person_path: str,
        cloth_path: str,
        cloth_type: str,
):
    update_job(job_id, JobStatus.RUNNING)
    try:
        svc = TryonService.get_instance()
        result_path = svc.run(job_id, person_path, cloth_path, cloth_type)
        result_url  = f"{settings.RESULT_BASE_URL}/{job_id}.png"
        update_job(job_id, JobStatus.DONE, result_url=result_url)
    except Exception as e:
        update_job(job_id, JobStatus.FAILED, error=str(e))
        print(f"[ERROR] job {job_id} failed: {e}")


# ── POST /api/jobs  (추론 요청 생성) ─────────────────
@router.post("", status_code=202)
async def create_job_ep(
        background_tasks: BackgroundTasks,
        person_image: UploadFile = File(...),
        cloth_image:  UploadFile = File(...),
        cloth_type:   str        = Form("upper"),
):
    job = create_job()

    person_path = os.path.join(UPLOAD_DIR, f"{job.job_id}_person.png")
    cloth_path  = os.path.join(UPLOAD_DIR, f"{job.job_id}_cloth.png")

    for path, upload in [(person_path, person_image), (cloth_path, cloth_image)]:
        with open(path, "wb") as f:
            f.write(await upload.read())

    background_tasks.add_task(
        _run_tryon_background,
        job.job_id, person_path, cloth_path, cloth_type
    )
    return {"job_id": job.job_id, "status": job.status}


# ── GET /api/jobs/{job_id}  (상태 폴링) ──────────────
@router.get("/{job_id}")
def get_job_ep(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id":     job.job_id,
        "status":     job.status,
        "result_url": job.result_url,
        "error":      job.error,
    }


# ── GET /api/jobs/{job_id}/result  (결과만) ──────────
@router.get("/{job_id}/result")
def get_job_result_ep(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in (JobStatus.PENDING, JobStatus.RUNNING):
        raise HTTPException(status_code=202, detail="Job still processing")
    return {
        "job_id":     job.job_id,
        "status":     job.status,
        "result_url": job.result_url,
        "error":      job.error,
    }