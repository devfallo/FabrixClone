from __future__ import annotations

import uuid
from typing import Any, Dict, List

from app.models.schemas import ToolManifest, ToolRunRequest, ToolRunResult


class ToolService:
    def __init__(self) -> None:
        self._manifests: Dict[str, ToolManifest] = {}
        self._runs: Dict[str, ToolRunResult] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            ToolManifest(
                name="grid.setFilter",
                description="Apply filter to a grid",
                input_schema={
                    "type": "object",
                    "properties": {"gridId": {"type": "string"}, "filters": {"type": "array"}},
                    "required": ["gridId", "filters"],
                },
                output_schema={"type": "object", "properties": {"applied": {"type": "boolean"}}},
                permissions=["tool:grid:filter"],
                audit_tags=["ui", "grid"],
            )
        )
        self.register(
            ToolManifest(
                name="grid.setSort",
                description="Apply sort to a grid",
                input_schema={
                    "type": "object",
                    "properties": {"gridId": {"type": "string"}, "sorts": {"type": "array"}},
                    "required": ["gridId", "sorts"],
                },
                output_schema={"type": "object", "properties": {"applied": {"type": "boolean"}}},
                permissions=["tool:grid:sort"],
                audit_tags=["ui", "grid"],
            )
        )
        self.register(
            ToolManifest(
                name="grid.setGroup",
                description="Apply grouping to a grid",
                input_schema={
                    "type": "object",
                    "properties": {"gridId": {"type": "string"}, "groups": {"type": "array"}},
                    "required": ["gridId", "groups"],
                },
                output_schema={"type": "object", "properties": {"applied": {"type": "boolean"}}},
                permissions=["tool:grid:group"],
                audit_tags=["ui", "grid"],
            )
        )

    def register(self, manifest: ToolManifest) -> None:
        self._manifests[manifest.name] = manifest

    def list_manifests(self) -> List[ToolManifest]:
        return list(self._manifests.values())

    def get_manifest(self, name: str) -> ToolManifest:
        return self._manifests[name]

    def validate_args(self, manifest: ToolManifest, args: Dict[str, Any]) -> None:
        schema = manifest.input_schema
        required = schema.get("required", [])
        for field in required:
            if field not in args:
                raise ValueError(f"Missing required field: {field}")

    def create_action(self, tool: str, args: Dict[str, Any], run_id: str) -> ToolRunRequest:
        manifest = self.get_manifest(tool)
        self.validate_args(manifest, args)
        return ToolRunRequest(run_id=run_id, action_id=str(uuid.uuid4()), tool=tool, args=args)

    def record_result(self, result: ToolRunResult) -> None:
        self._runs[result.action_id] = result

    def list_results(self, run_id: str) -> List[ToolRunResult]:
        return [r for r in self._runs.values() if r.run_id == run_id]
