from __future__ import annotations

import uuid
from typing import Dict, List

from app.models.schemas import AssetCreateRequest, AssetResponse


class AssetService:
    def __init__(self) -> None:
        self._assets: Dict[str, AssetResponse] = {}

    def create(self, request: AssetCreateRequest) -> AssetResponse:
        asset_id = str(uuid.uuid4())
        asset = AssetResponse(
            id=asset_id,
            asset_type=request.asset_type,
            name=request.name,
            version=request.version,
            payload=request.payload,
            status=request.status,
        )
        self._assets[asset_id] = asset
        return asset

    def list_assets(self) -> List[AssetResponse]:
        return list(self._assets.values())
