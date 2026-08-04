from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from captain_core.errors import ManifestError
from captain_core.models import ResolvedManifest
from .header import parse_manifest_header, validate_manifest_ownership
from .resolver import resolve_manifest


def load_manifest_document(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path).expanduser().resolve()
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as error:
        raise ManifestError(f"Unable to read manifest {manifest_path}: {error}") from error
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ManifestError(
            f"Invalid JSON in {manifest_path}: line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error
    if not isinstance(document, dict):
        raise ManifestError("Manifest root must be a JSON object.")
    return document


def load_tool_manifest(reference: str | Path, *, tool: str, start: str | Path | None = None, captain_root: str | Path | None = None) -> ResolvedManifest:
    path = resolve_manifest(reference, tool=tool, start=start, captain_root=captain_root)
    document = load_manifest_document(path)
    header = parse_manifest_header(document)
    validate_manifest_ownership(header, tool)
    return ResolvedManifest(path=path, header=header, document=document)
