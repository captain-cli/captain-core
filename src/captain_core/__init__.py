"""Shared foundation for the Captain tool ecosystem."""

from .errors import CaptainCoreError, CaptainProjectNotFoundError, ManifestError, ManifestNotFoundError, ManifestOwnershipError
from .models import ManifestHeader, ResolvedCaptainManifest, ResolvedManifest, ResolvedToolConfig
from .project_manifest import (
    CAPTAIN_MANIFEST_FILENAME,
    CAPTAIN_MANIFEST_SCHEMA,
    CAPTAIN_TOOL_MANIFEST_SCHEMA,
    get_captain_manifest_path,
    get_manifest_section,
    get_project_root,
    load_captain_manifest,
    resolve_tool_config,
    validate_captain_manifest,
)

__all__ = [
    "CaptainCoreError",
    "CaptainProjectNotFoundError",
    "ManifestError",
    "ManifestNotFoundError",
    "ManifestOwnershipError",
    "ManifestHeader",
    "ResolvedCaptainManifest",
    "ResolvedManifest",
    "ResolvedToolConfig",
    "CAPTAIN_MANIFEST_FILENAME",
    "CAPTAIN_MANIFEST_SCHEMA",
    "CAPTAIN_TOOL_MANIFEST_SCHEMA",
    "get_captain_manifest_path",
    "get_manifest_section",
    "get_project_root",
    "load_captain_manifest",
    "resolve_tool_config",
    "validate_captain_manifest",
]

__version__ = "0.1.0"
