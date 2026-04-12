# app/schemas/jobs_schemas.py
from enum import Enum
from pydantic import BaseModel


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CreateJobRequest(BaseModel):
    human_path: str
    cloth_path: str


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus
    result_url: str | None = None
    error_message: str | None = None


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobResultResponse(BaseModel):
    job_id: str
    status: JobStatus
    result_url: str | None = None
    error_message: str | None = None