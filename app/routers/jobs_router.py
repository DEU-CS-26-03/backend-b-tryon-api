# app/routers/jobs_router.py
from fastapi import APIRouter, HTTPException

from app.schemas.jobs_schemas import (
    CreateJobRequest, JobCreateResponse, JobResponse, JobResultResponse,
)
from app.services.jobs_service import create_job, get_job, get_job_result

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobCreateResponse)
async def create_job_ep(body: CreateJobRequest):
    return await create_job(body)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_ep(job_id: str):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job["job_id"], "status": job["status"]}


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result_ep(job_id: str):
    job = await get_job_result(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "result_url": job["result_url"],
        "error_message": job["error_message"],
    }