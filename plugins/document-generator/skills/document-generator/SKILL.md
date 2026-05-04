---
name: document-generator
description: Use for Brandon Gottshall's About-Me repo when validating YAML, generating official PDFs, exporting portfolio data, drafting tailored resume/CV/cover-letter variants, or archiving custom generation runs with full provenance.
---

# Document Generator

## Repo Contract

- Treat `content/` as the source of truth for official profile facts.
- Validate before generating: `make validate`.
- Rebuild official public outputs with `make all`.
- Refresh portfolio data with `make export`.
- Run `make privacy-scan` before committing or publishing.
- Raw job-specific generation runs must be archived in the private companion repo configured by `CUSTOM_GENERATION_ARCHIVE_ROOT`.

## Official Document Workflow

1. Inspect relevant YAML in `content/` and `config/`.
2. Make minimal source-data or template changes.
3. Run:

```bash
make validate
make test
make all
make export
make privacy-scan
```

4. Render PDFs with `pdftoppm` if layout changed.

## Tailored Generation Workflow

1. Store the job description in the private archive target, not this public repo.
2. Select source facts from `content/`; do not invent credentials or metrics.
3. Draft tailored outputs in the private archive target first.
4. If an artifact should become official, promote the source edits into `content/` and rebuild official PDFs.
5. If an artifact should become a public example, sanitize it according to `docs/ARCHIVE_CONTRACT.md`.

## Archive Helper

Use the plugin helper only after setting a private archive root:

```bash
export CUSTOM_GENERATION_ARCHIVE_ROOT=/path/to/private/about-me-generations
python plugins/document-generator/scripts/archive_generation.py \
  --company "Example Company" \
  --role "Example Role" \
  --job-description /path/to/job-description.md
```

The helper creates a run directory, copies inputs, records source commit, writes
`manifest.json`, and validates it against
`schemas/archive/custom-generation-run.schema.json`.

## Prompt Templates

Shared between the Codex and Claude Code surfaces; edit in one place:

- `../../../../prompts/document-generator/tailored-system.md`
- `../../../../prompts/document-generator/tailored-task.md`
- `../../../../prompts/document-generator/archive-checklist.md`
