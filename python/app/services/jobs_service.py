# python/app/services/jobs_service.py
import uuid
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, field

class JobStatus(str, Enum):
    PENDING  = "PENDING"
    RUNNING  = "RUNNING"
    DONE     = "DONE"
    FAILED   = "FAILED"

@dataclass
class Job:
    job_id: str
    status: JobStatus = JobStatus.PENDING
    result_url: Optional[str] = None
    error: Optional[str] = None

# 인메모리 저장소 (졸업 작품 수준에서는 충분, 이후 Redis 연동 가능)
_jobs: Dict[str, Job] = {}

def create_job() -> Job:
    job = Job(job_id=str(uuid.uuid4()))
    _jobs[job.job_id] = job
    return job

def get_job(job_id: str) -> Optional[Job]:
    return _jobs.get(job_id)

def update_job(job_id: str, status: JobStatus, result_url=None, error=None):
    job = _jobs.get(job_id)
    if job:
        job.status = status
        if result_url: job.result_url = result_url
        if error:      job.error = error