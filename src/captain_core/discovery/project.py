from __future__ import annotations

import os
from pathlib import Path

from captain_core.errors import CaptainProjectNotFoundError

CAPTAIN_DIRECTORY_NAME = "captain"


def find_project_root(start: str | Path | None = None) -> Path:
    current = Path(start or Path.cwd()).expanduser().resolve()
    for candidate in (current, *current.parents):
        if (candidate / CAPTAIN_DIRECTORY_NAME).is_dir():
            return candidate
    raise CaptainProjectNotFoundError(
        f'Unable to locate a "{CAPTAIN_DIRECTORY_NAME}" directory from {current} or any parent directory.'
    )


def find_captain_root(start: str | Path | None = None) -> Path:
    configured = os.environ.get("CAPTAIN_ROOT")
    if configured:
        captain_root = Path(configured).expanduser().resolve()
        if not captain_root.is_dir():
            raise CaptainProjectNotFoundError(
                f"CAPTAIN_ROOT does not exist or is not a directory: {captain_root}"
            )
        return captain_root
    return find_project_root(start) / CAPTAIN_DIRECTORY_NAME
