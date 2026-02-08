from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from app.models.schemas import LabJobCreateRequest, LabJobResponse
from app.services.rag_service import RAGService


class LabService:
    def __init__(self, rag_service: RAGService) -> None:
        self._rag_service = rag_service
        self._jobs: Dict[str, LabJobResponse] = {}

    def create_job(self, request: LabJobCreateRequest) -> LabJobResponse:
        job_id = str(uuid.uuid4())
        job = LabJobResponse(job_id=job_id, status="queued", message=None, created_at=datetime.utcnow())
        self._jobs[job_id] = job
        return job

    def run_job(self, job_id: str, request: LabJobCreateRequest) -> LabJobResponse:
        job = self._jobs[job_id]
        running = job.model_copy(update={"status": "running"})
        self._jobs[job_id] = running
        try:
            self._rag_service.add_document(
                request.kb_id,
                request.title,
                request.text,
                request.source_uri,
                request.page,
                request.acl,
            )
            completed = running.model_copy(update={"status": "completed", "message": "indexed"})
            self._jobs[job_id] = completed
            return completed
        except Exception as exc:  # pragma: no cover - defensive
            failed = running.model_copy(update={"status": "failed", "message": str(exc)})
            self._jobs[job_id] = failed
            return failed

    def get_job(self, job_id: str) -> LabJobResponse:
        return self._jobs[job_id]
