# /services/jobs_service.py
import uuid
from datetime import datetime

from app.schemas.jobs_schemas import CreateJobRequest, JobStatus

# vton/scripts/vton.py 에 run_tryon_real 이 정의되어 있다고 가정
# from vton.scripts.vton import run_tryon_real 는 정의되고 주석 해제

_JOBS: dict[str, dict] = {}


async def create_job(req: CreateJobRequest) -> dict:
    job_id = str(uuid.uuid4())
    _JOBS[job_id] = {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "created_at": datetime.utcnow(),
        "result_url": None,
        "error_message": None,
        "human_path": req.human_path,
        "cloth_path": req.cloth_path,
    }

    try:
        _JOBS[job_id]["status"] = JobStatus.PROCESSING
        _, result_path = await run_tryon_real(req)
        _JOBS[job_id]["status"] = JobStatus.COMPLETED
        _JOBS[job_id]["result_url"] = result_path
    except Exception as e:
        _JOBS[job_id]["status"] = JobStatus.FAILED
        _JOBS[job_id]["error_message"] = str(e)

    return _JOBS[job_id]  # ← { dict } 가 아닌 dict 반환


async def get_job(job_id: str) -> dict | None:
    return _JOBS.get(job_id)


async def get_job_result(job_id: str) -> dict | None:
    return _JOBS.get(job_id)