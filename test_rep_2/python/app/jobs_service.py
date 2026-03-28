# app/jobs_service.py
import uuid
from datetime import datetime
from .jobs_schemas import JobStatus
from ..vton.vton import run_tryon_real   # 너가 이미 만든 real 파이프라인

# 메모리 임시 저장 (나중에 Redis로 교체 가능)
_JOBS: dict[str, dict] = {}

async def create_job(req):
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

    # 간단 버전: 백그라운드로 바로 처리 (FastAPI BackgroundTasks 써도 됨)
    # 여기서는 sync 예시
    try:
        _JOBS[job_id]["status"] = JobStatus.PROCESSING
        _, result_path = run_tryon_real(req)  # result_path: "/results/{job_id}/output.png"
        _JOBS[job_id]["status"] = JobStatus.COMPLETED
        _JOBS[job_id]["result_url"] = result_path
    except Exception as e:
        _JOBS[job_id]["status"] = JobStatus.FAILED
        _JOBS[job_id]["error_message"] = str(e)

    return {
        _JOBS[job_id]
    }

async def get_job(job_id: str):
    return _JOBS.get(job_id)

async def get_job_result(job_id: str):
    return _JOBS.get(job_id)
