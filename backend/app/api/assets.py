from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import AssetCreateRequest, AssetResponse
from app.services.asset_service import AssetService


router = APIRouter()


def get_asset_service() -> AssetService:
    from app.main import asset_service

    return asset_service


@router.post("/v1/assets", response_model=AssetResponse)
async def create_asset(
    request: AssetCreateRequest,
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    return asset_service.create(request)


@router.get("/v1/assets", response_model=list[AssetResponse])
async def list_assets(
    asset_service: AssetService = Depends(get_asset_service),
) -> list[AssetResponse]:
    return asset_service.list_assets()
