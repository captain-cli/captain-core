# Captain manifest conformance

Canonical project root: `manifest.json` (`captain/manifest/v1`).
Tool configuration is either an inline object under its tool name or a
`manifests.<tool>` relative path to a `captain/tool-manifest/v1` envelope
with matching `tool` and an object-valued `config`, never both.
References must stay within the project root, including symlink resolution.
The separate signed Outfit Registry is not a Captain project manifest.

Fixtures in `cases.json` describe shared acceptance/rejection expectations.
