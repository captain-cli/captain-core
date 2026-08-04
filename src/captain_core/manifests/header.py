from __future__ import annotations

from typing import Any

from captain_core.errors import ManifestError, ManifestOwnershipError
from captain_core.models import ManifestHeader

_REQUIRED = ("id", "name", "tool", "category", "schemaVersion", "manifestVersion")


def parse_manifest_header(document: dict[str, Any]) -> ManifestHeader:
    raw = document.get("header")
    if not isinstance(raw, dict):
        raise ManifestError('Manifest property "header" must be an object.')
    values: dict[str, str] = {}
    for field in _REQUIRED:
        value = raw.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ManifestError(f'Manifest header property "{field}" must be a non-empty string.')
        values[field] = value.strip()
    return ManifestHeader(
        id=values["id"],
        name=values["name"],
        tool=values["tool"],
        category=values["category"],
        schema_version=values["schemaVersion"],
        manifest_version=values["manifestVersion"],
    )


def validate_manifest_ownership(header: ManifestHeader, expected_tool: str) -> None:
    if header.tool != expected_tool:
        raise ManifestOwnershipError(
            f'Manifest "{header.id}" belongs to tool "{header.tool}", not "{expected_tool}".'
        )
