from __future__ import annotations

from pathlib import Path

from captain_core.errors import ManifestError


def validate_relative_reference(value: str, field_name: str = "reference") -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{field_name} must be a non-empty string.")
    normalized = value.replace("\\", "/").strip("/")
    candidate = Path(normalized)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ManifestError(f"{field_name} must remain inside its configured root: {value}")
    if not candidate.parts:
        raise ManifestError(f"{field_name} resolves to an empty path.")
    return candidate


def resolve_inside_root(root: Path, relative_path: Path) -> Path:
    resolved_root = root.expanduser().resolve()
    target = (resolved_root / relative_path).resolve()
    if target != resolved_root and resolved_root not in target.parents:
        raise ManifestError(f"Path escapes configured root: {relative_path}")
    return target
