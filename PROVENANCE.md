# Provenance and License Map

This repository is Brandon Gottshall's official document-generation system. It
started as a fork of [Awesome CV](https://github.com/posquit0/Awesome-CV), but
the current public purpose is a YAML-driven personal document pipeline.

## License Boundaries

| Area | Status | License posture |
| --- | --- | --- |
| `src/awesome-cv.cls` | Derived from Awesome CV | LPPL v1.3c. See `LICENCE` and the file header. |
| Base LaTeX template lineage in `templates/` | Adapted from Awesome CV examples and local work | Preserve Awesome CV credit; do not treat as whole-repo MIT until this lineage is replaced. |
| `document_pipeline/`, `scripts/`, `schemas/`, `tests/`, `plugins/`, `.agents/` | Brandon-authored pipeline/tooling unless otherwise noted | MIT under `LICENSE`. |
| `docs/`, `README.md`, `AGENTS.md`, `handoff/` | Brandon-authored repository documentation | MIT under `LICENSE`, excluding quoted third-party license text. |
| `content/` | Brandon's personal source data | Public portfolio content, not a reusable sample identity. |
| `output/` and `exports/` | Generated from Brandon's personal source data | Public portfolio artifacts, not generic template examples. |
| `examples/` | Upstream examples and historical local examples | Retain original provenance where applicable; do not use as official personal output. |

## Why This Is Not Whole-Repo MIT Yet

The generator, schemas, docs, plugin, and workflow contracts are Brandon-owned
software and documentation. The visual foundation still includes Awesome CV
assets and derivative LaTeX template lineage. Treating the entire repository as
MIT would blur that boundary.

Whole-repo MIT becomes appropriate only after the inherited Awesome CV class and
template lineage are replaced or isolated behind a clearly separate dependency.

## Fork Detachment

After the license map, README, schemas, plugin, archive contract, exports, and
verification workflow are in place and pushed, this repository is a reasonable
candidate for GitHub fork detachment. Detachment is a GitHub account/support
action and should be done intentionally because it is permanent.
