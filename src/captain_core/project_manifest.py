from __future__ import annotations

from pathlib import Path
from typing import Any

from captain_core.errors import ManifestError, ManifestNotFoundError, ManifestOwnershipError
from captain_core.filesystem import resolve_inside_root, validate_relative_reference
from captain_core.manifests.loader import load_manifest_document
from captain_core.models import ResolvedCaptainManifest, ResolvedToolConfig

CAPTAIN_MANIFEST_FILENAME = "manifest.json"
CAPTAIN_MANIFEST_SCHEMA = "captain/manifest/v1"
CAPTAIN_TOOL_MANIFEST_SCHEMA = "captain/tool-manifest/v1"


def get_project_root(start: str | Path | None = None) -> Path:
    root = Path(start or Path.cwd()).expanduser().resolve()
    if not root.is_dir():
        raise ManifestNotFoundError(f"Captain project directory does not exist: {root}")
    return root


def get_captain_manifest_path(
    *,
    start: str | Path | None = None,
    captain_root: str | Path | None = None,
) -> Path:
    # captain_root is retained as a compatibility alias for callers that already
    # pass an explicit root. The canonical root is now the project directory.
    root = get_project_root(captain_root if captain_root is not None else start)
    return root / CAPTAIN_MANIFEST_FILENAME


def validate_captain_manifest(document: dict[str, Any]) -> None:
    schema = document.get("schema")
    if schema != CAPTAIN_MANIFEST_SCHEMA:
        raise ManifestError(
            f'Unsupported Captain manifest schema: {schema!r}. '
            f'Expected "{CAPTAIN_MANIFEST_SCHEMA}".'
        )

    project = document.get("project")
    if not isinstance(project, dict):
        raise ManifestError('Captain manifest property "project" must be an object.')

    for field in ("name", "type", "version"):
        value = project.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ManifestError(
                f'Captain manifest property "project.{field}" must be a non-empty string.'
            )

    version_lanes = document.get("versionLanes", {})
    if not isinstance(version_lanes, dict):
        raise ManifestError('Captain manifest property "versionLanes" must be an object.')

    components = document.get("components", [])
    if not isinstance(components, list):
        raise ManifestError('Captain manifest property "components" must be an array.')

    if "packaging" in document:
        raise ManifestError(
            'Deprecated Captain manifest property "packaging" is no longer supported; '
            'configure first-class "stager" and "embark" sections instead.'
        )

    manifests = document.get("manifests", {})
    if not isinstance(manifests, dict):
        raise ManifestError('Captain manifest property "manifests" must be an object.')
    for tool, reference in manifests.items():
        if not isinstance(tool, str) or not tool.strip():
            raise ManifestError('Captain manifest "manifests" keys must be non-empty strings.')
        validate_relative_reference(reference, f'manifests.{tool}')


def load_captain_manifest(
    *,
    start: str | Path | None = None,
    captain_root: str | Path | None = None,
) -> ResolvedCaptainManifest:
    path = get_captain_manifest_path(start=start, captain_root=captain_root)
    if not path.is_file():
        raise ManifestNotFoundError(f"Captain manifest does not exist: {path}")
    document = load_manifest_document(path)
    validate_captain_manifest(document)
    return ResolvedCaptainManifest(path=path, document=document)


def get_manifest_section(
    document: dict[str, Any],
    section: str,
    *,
    required: bool = False,
) -> dict[str, Any] | None:
    if not isinstance(section, str) or not section.strip():
        raise ManifestError("Captain manifest section name must be a non-empty string.")

    key = section.strip()
    value = document.get(key)

    if value is None:
        if required:
            raise ManifestError(f'Captain manifest section "{key}" is required.')
        return None

    if not isinstance(value, dict):
        raise ManifestError(f'Captain manifest section "{key}" must be an object.')

    return value


def _load_referenced_tool_config(
    project_root: Path,
    *,
    tool: str,
    reference: str,
) -> ResolvedToolConfig:
    relative = validate_relative_reference(reference, f'manifests.{tool}')
    path = resolve_inside_root(project_root, relative)
    if not path.is_file():
        raise ManifestNotFoundError(
            f'Captain manifest reference for tool "{tool}" does not exist: {path}'
        )

    document = load_manifest_document(path)
    schema = document.get("schema")
    if schema != CAPTAIN_TOOL_MANIFEST_SCHEMA:
        raise ManifestError(
            f'Unsupported Captain tool manifest schema for "{tool}": {schema!r}. '
            f'Expected "{CAPTAIN_TOOL_MANIFEST_SCHEMA}".'
        )

    owner = document.get("tool")
    if owner != tool:
        raise ManifestOwnershipError(
            f'Captain tool manifest {path} belongs to "{owner}", not "{tool}".'
        )

    config = document.get("config")
    if not isinstance(config, dict):
        raise ManifestError(
            f'Captain tool manifest property "config" for "{tool}" must be an object.'
        )

    return ResolvedToolConfig(tool=tool, path=path, config=config, inline=False)


def resolve_tool_config(
    tool: str,
    *,
    start: str | Path | None = None,
    captain_root: str | Path | None = None,
    required: bool = False,
) -> ResolvedToolConfig | None:
    if not isinstance(tool, str) or not tool.strip():
        raise ManifestError("Captain tool name must be a non-empty string.")
    key = tool.strip()

    resolved = load_captain_manifest(start=start, captain_root=captain_root)
    project_root = resolved.path.parent
    inline = get_manifest_section(resolved.document, key)
    manifests = resolved.document.get("manifests", {})
    reference = manifests.get(key)

    if inline is not None and reference is not None:
        raise ManifestError(
            f'Captain tool "{key}" is configured both inline and through manifests.{key}; '
            "choose one source of truth for that tool."
        )

    if inline is not None:
        return ResolvedToolConfig(
            tool=key,
            path=resolved.path,
            config=inline,
            inline=True,
        )

    if reference is not None:
        return _load_referenced_tool_config(
            project_root,
            tool=key,
            reference=reference,
        )

    if required:
        raise ManifestError(f'Captain tool configuration "{key}" is required.')
    return None
