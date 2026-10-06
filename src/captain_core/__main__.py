from __future__ import annotations

import argparse
import json
import sys

from captain_core.errors import CaptainCoreError
from captain_core.project_manifest import resolve_tool_config


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="captain-core")
    subparsers = parser.add_subparsers(dest="command", required=True)
    manifest = subparsers.add_parser("manifest", help="Work with Captain-owned manifests")
    manifest_sub = manifest.add_subparsers(dest="manifest_command", required=True)
    resolve = manifest_sub.add_parser("resolve", help="Resolve a tool configuration")
    resolve.add_argument("--project", required=True, help="Captain project directory")
    resolve.add_argument("--tool", required=True, help="Captain ecosystem tool name")
    resolve.add_argument("--required", action="store_true", help="Fail when the tool is not configured")
    resolve.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        resolved = resolve_tool_config(
            args.tool,
            start=args.project,
            required=args.required,
        )
        payload = None if resolved is None else {
            "tool": resolved.tool,
            "path": str(resolved.path),
            "inline": resolved.inline,
            "config": resolved.config,
        }
        if args.json:
            print(json.dumps(payload, separators=(",", ":")))
        elif resolved is None:
            print(f'{args.tool}: not configured')
        else:
            print(f'{resolved.tool}: {resolved.path}')
        return 0
    except CaptainCoreError as error:
        print(f"captain-core: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
