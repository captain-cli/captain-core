# Captain Core

`captain-core` provides the shared foundation used by the Captain ecosystem.

Captain Core owns the cross-tool contracts that must remain consistent across Captain, Stager, Embark, Dockhand, ServiceWright, and future ecosystem tools: project discovery, the canonical Captain manifest location, manifest loading and validation, shared path safety, and common models/errors.

## Canonical project manifest

A Captain project has one Captain-owned source manifest:

```text
project/
└── manifest.json
```

The canonical schema identifier is:

```text
captain/manifest/v1
```

Tool configuration lives in named sections of that one document instead of separate project manifests:

```json
{
  "schema": "captain/manifest/v1",
  "project": {
    "name": "example",
    "type": "native",
    "version": "1.0.0"
  },
  "versionLanes": {},
  "components": [],
  "system": {},
  "build": {},
  "stager": {},
  "embark": {},
  "dockhand": {},
  "servicewright": {}
}
```

Captain Core owns locating and loading the document. Each ecosystem tool owns the semantics of its own section.

## Legacy tool manifests

The existing `captain/manifests/<tool>/...` APIs remain available during migration for standalone tool manifests and compatibility. New project-level configuration should converge on the project-root `manifest.json`.

## Development install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Tool integration

```python
from captain_core import get_manifest_section, load_captain_manifest

resolved = load_captain_manifest()
service = get_manifest_section(
    resolved.document,
    "servicewright",
    required=True,
)
```

Standalone compatibility manifests can still use:

```python
from captain_core.manifests import load_tool_manifest

resolved = load_tool_manifest(
    "filesystems/omni-shell-demo",
    tool="stager",
)
```

Captain ecosystem Python tools should declare:

```toml
dependencies = [
  "captain-core>=0.1,<0.2"
]
```


## Captain-owned project manifests

The canonical Captain project manifest lives at the project root:

```text
<project root>/
├── manifest.json
└── manifests/
    ├── build.json
    ├── stager.json
    ├── embark.json
    ├── dockhand.json
    ├── servicewright.json
    └── schemawright.json
```

`manifest.json` is always authoritative. Tool configuration may be inline, referenced from a Captain-owned file under `manifests/`, or mixed in a hybrid layout. Captain Core resolves both forms into the same tool configuration contract.

Referenced tool files use the `captain/tool-manifest/v1` envelope, declare their tool owner, and contain a `config` object. Captain Core validates the shared envelope and path ownership; the consuming tool validates the semantics of `config`.
