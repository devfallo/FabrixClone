from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import AuditLogEntry, PolicyEvent, RoleCreateRequest, UsageStats, UserCreateRequest
from app.services.audit_service import AuditService
from app.services.admin_service import AdminService
from app.services.policy_service import PolicyService


router = APIRouter()


def get_admin_service() -> AdminService:
    from app.main import admin_service

    return admin_service


def get_audit_service() -> AuditService:
    from app.main import audit_service

    return audit_service


def get_policy_service() -> PolicyService:
    from app.main import policy_service

    return policy_service


@router.post("/v1/admin/roles")
async def create_role(
    request: RoleCreateRequest,
    admin_service: AdminService = Depends(get_admin_service),
) -> dict:
    admin_service.create_role(request)
    return {"status": "created"}


@router.post("/v1/admin/users")
async def create_user(
    request: UserCreateRequest,
    admin_service: AdminService = Depends(get_admin_service),
) -> dict:
    admin_service.create_user(request)
    return {"status": "created"}


@router.get("/v1/admin/usage", response_model=UsageStats)
async def usage(
    admin_service: AdminService = Depends(get_admin_service),
) -> UsageStats:
    return admin_service.usage_stats()


@router.get("/v1/admin/audit", response_model=list[AuditLogEntry])
async def audit_logs(
    audit_service: AuditService = Depends(get_audit_service),
) -> list[AuditLogEntry]:
    return audit_service.list_entries()


@router.get("/v1/admin/policies/events", response_model=list[PolicyEvent])
async def policy_events(
    policy_service: PolicyService = Depends(get_policy_service),
) -> list[PolicyEvent]:
    return policy_service.list_events()
