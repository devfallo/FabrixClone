from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import RoleCreateRequest, UsageStats, UserCreateRequest
from app.services.admin_service import AdminService


router = APIRouter()


def get_admin_service() -> AdminService:
    from app.main import admin_service

    return admin_service


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
