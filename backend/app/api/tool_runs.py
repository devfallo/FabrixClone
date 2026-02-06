from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import ToolRunResult
from app.services.admin_service import AdminService
from app.services.tool_service import ToolService


router = APIRouter()


def get_tool_service() -> ToolService:
    from app.main import tool_service

    return tool_service


def get_admin_service() -> AdminService:
    from app.main import admin_service

    return admin_service


@router.post("/v1/tools/action-result")
async def action_result(
    result: ToolRunResult,
    tool_service: ToolService = Depends(get_tool_service),
    admin_service: AdminService = Depends(get_admin_service),
) -> dict:
    tool_service.record_result(result)
    admin_service.increment_usage("tool_runs")
    return {"status": "recorded"}
