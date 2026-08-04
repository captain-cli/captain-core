class CaptainCoreError(Exception):
    """Base error for expected Captain Core failures."""


class CaptainProjectNotFoundError(CaptainCoreError):
    """Raised when no project-local captain directory can be found."""


class ManifestError(CaptainCoreError):
    """Raised when a manifest is malformed or unsafe."""


class ManifestNotFoundError(ManifestError):
    """Raised when a manifest reference cannot be resolved."""


class ManifestOwnershipError(ManifestError):
    """Raised when a manifest belongs to a different Captain tool."""
