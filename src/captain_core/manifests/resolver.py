from __future__ import annotations

from pathlib import Path

from captain_core.discovery import find_captain_root
from captain_core.errors import ManifestNotFoundError
from captain_core.filesystem import resolve_inside_root, validate_relative_reference


def get_tool_manifest_root(tool: str, *, start: str | Path | None = None, captain_root: str | Path | None = None) -> Path:
    if not tool or not tool.strip():
        raise ManifestNotFoundError("Tool name must be provided.")
    root = Path(captain_root).expanduser().resolve() if captain_root is not None else find_captain_root(start)
    return root / "manifests" / tool.strip()


def resolve_manifest(reference: str | Path, *, tool: str, start: str | Path | None = None, captain_root: str | Path | None = None) -> Path:
    supplied = Path(reference).expanduser()
    if supplied.is_absolute():
        candidate = supplied.resolve()
        if candidate.is_file():
            return candidate
        raise ManifestNotFoundError(f"Manifest file does not exist: {candidate}")

    explicit_candidate = (Path.cwd() / supplied).resolve()
    if explicit_candidate.is_file():
        return explicit_candidate

    relative_reference = validate_relative_reference(str(reference))
    if relative_reference.suffix.lower() != ".json":
        relative_reference = relative_reference.with_suffix(".json")

    manifest_root = get_tool_manifest_root(tool, start=start, captain_root=captain_root).resolve()
    candidate = resolve_inside_root(manifest_root, relative_reference)
    if not candidate.is_file():
        raise ManifestNotFoundError(
            f'Unable to locate manifest "{reference}" for tool "{tool}". Searched: {candidate}'
        )
    return candidate
