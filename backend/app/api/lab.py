from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import LabJobCreateRequest, LabJobResponse
from app.services.lab_service import LabService


router = APIRouter()


def get_lab_service() -> LabService:
    from app.main import lab_service

    return lab_service


@router.post("/v1/lab/jobs", response_model=LabJobResponse)
async def create_job(
    request: LabJobCreateRequest,
    lab_service: LabService = Depends(get_lab_service),
) -> LabJobResponse:
    return lab_service.create_job(request)


@router.post("/v1/lab/jobs/{job_id}/run", response_model=LabJobResponse)
async def run_job(
    job_id: str,
    request: LabJobCreateRequest,
    lab_service: LabService = Depends(get_lab_service),
) -> LabJobResponse:
    return lab_service.run_job(job_id, request)


@router.get("/v1/lab/jobs/{job_id}", response_model=LabJobResponse)
async def get_job(
    job_id: str,
    lab_service: LabService = Depends(get_lab_service),
) -> LabJobResponse:
    return lab_service.get_job(job_id)
