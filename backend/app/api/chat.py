from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import ChatMessageRequest, ChatMessageResponse
from app.orchestrator.contracts import RunContext
from app.orchestrator.engine import OrchestratorEngine
from app.services.admin_service import AdminService
from app.services.state_service import StateService


router = APIRouter()


def get_engine() -> OrchestratorEngine:
    from app.main import engine

    return engine


def get_state_service() -> StateService:
    from app.main import state_service

    return state_service


def get_admin_service() -> AdminService:
    from app.main import admin_service

    return admin_service


@router.post("/v1/chat/message", response_model=ChatMessageResponse)
async def chat_message(
    request: ChatMessageRequest,
    engine: OrchestratorEngine = Depends(get_engine),
    state_service: StateService = Depends(get_state_service),
    admin_service: AdminService = Depends(get_admin_service),
) -> ChatMessageResponse:
    ui_state = state_service.get_state(request.session_id)
    roles = admin_service.user_permissions(request.user_id)
    ctx = RunContext(
        session_id=request.session_id,
        conversation_id=request.conversation_id,
        agent_id=request.agent_id,
        user_id=request.user_id,
        tenant_id=request.tenant_id,
        message=request.message,
        ui_state=ui_state,
        policies={"roles": roles},
        tool_catalog=[],
        kb_id=ui_state.get("kb_id"),
    )
    return await engine.run(ctx)
