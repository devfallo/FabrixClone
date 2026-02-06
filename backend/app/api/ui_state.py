from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import UIStatePatchRequest, UIStatePatchResponse
from app.services.state_service import StateService


router = APIRouter()


def get_state_service() -> StateService:
    from app.main import state_service

    return state_service


@router.post("/v1/ui/state", response_model=UIStatePatchResponse)
async def patch_state(
    request: UIStatePatchRequest,
    state_service: StateService = Depends(get_state_service),
) -> UIStatePatchResponse:
    event = state_service.apply_patch(request.session_id, request.ui_state_patch, request.version)
    return UIStatePatchResponse(
        session_id=request.session_id,
        version=event["version"],
        updated_at=event["updated_at"],
    )
