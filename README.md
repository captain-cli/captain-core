# Captain Core

`captain-core` provides the shared foundation used by Captain-family tools.

The first release standardizes project discovery, `captain/` discovery, tool-owned manifest roots, short manifest references, safe path handling, common manifest headers, and tool ownership validation.

## Project convention

```text
project/
└── captain/
    └── manifests/
        ├── stager/
        ├── schemawright/
        ├── servicewright/
        └── captain/
```

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
from captain_core.manifests import load_tool_manifest

resolved = load_tool_manifest(
    "filesystems/omni-shell-demo",
    tool="stager",
)
```

Captain and each standalone tool should declare:

```toml
dependencies = [
  "captain-core>=0.1,<0.2"
]
```
