from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ManifestHeader:
    id: str
    name: str
    tool: str
    category: str
    schema_version: str
    manifest_version: str


@dataclass(frozen=True)
class ResolvedManifest:
    path: Path
    header: ManifestHeader
    document: dict[str, Any]
