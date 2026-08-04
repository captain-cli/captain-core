"""Shared foundation for the Captain tool ecosystem."""

from .errors import CaptainCoreError, CaptainProjectNotFoundError, ManifestError, ManifestNotFoundError, ManifestOwnershipError
from .models import ManifestHeader, ResolvedManifest

__all__ = [
    "CaptainCoreError",
    "CaptainProjectNotFoundError",
    "ManifestError",
    "ManifestNotFoundError",
    "ManifestOwnershipError",
    "ManifestHeader",
    "ResolvedManifest",
]

__version__ = "0.1.0"
