from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseDocumentRequest,
    RAGQueryRequest,
    RAGQueryResponse,
)
from app.services.admin_service import AdminService
from app.services.audit_service import AuditService
from app.services.rag_service import RAGService


router = APIRouter()


def get_rag_service() -> RAGService:
    from app.main import rag_service

    return rag_service


def get_admin_service() -> AdminService:
    from app.main import admin_service

    return admin_service


def get_audit_service() -> AuditService:
    from app.main import audit_service

    return audit_service


@router.post("/v1/kb")
async def create_kb(
    request: KnowledgeBaseCreateRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> dict:
    kb_id = rag_service.create_kb(request.name, request.description, request.acl)
    return {"kb_id": kb_id}


@router.post("/v1/kb/{kb_id}/documents")
async def add_document(
    kb_id: str,
    request: KnowledgeBaseDocumentRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> dict:
    doc_id = rag_service.add_document(
        kb_id,
        request.title,
        request.text,
        request.source_uri,
        request.page,
        request.acl,
    )
    return {"doc_id": doc_id}


@router.post("/v1/rag/query", response_model=RAGQueryResponse)
async def rag_query(
    request: RAGQueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
    admin_service: AdminService = Depends(get_admin_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> RAGQueryResponse:
    admin_service.increment_usage("rag_queries")
    answer, citations = rag_service.query(request.kb_id, request.query, request.roles)
    audit_service.log(
        actor="system",
        action="rag.query",
        target=request.kb_id,
        meta={"query": request.query, "hits": len(citations)},
    )
    return RAGQueryResponse(answer=answer, citations=citations)
