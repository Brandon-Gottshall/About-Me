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
3. Cite selected facts as `content/<file>.yaml:<key>` or a more precise dotted key when needed.
4. Draft tailored outputs in the private archive target first.
5. If an artifact should become official, promote the source edits into `content/` and rebuild official PDFs.
6. If an artifact should become a public example, sanitize it according to `docs/ARCHIVE_CONTRACT.md`.

## Archive Helper

Use the plugin helper only after setting a private archive root:

```bash
source "$HOME/Documents/GitHub/about-me-generations/scripts/env.sh"
python plugins/document-generator/scripts/archive_generation.py \
  --company "Example Company" \
  --role "Example Role" \
  --job-description /path/to/job-description.md
```

The helper creates a run directory, copies inputs, records source commit, writes
`manifest.json`, and validates it against
`schemas/archive/custom-generation-run.schema.json`.

After adding prompts, selected facts, drafts, generated artifacts, or
verification notes, validate the private archive repo:

```bash
cd "$CUSTOM_GENERATION_ARCHIVE_ROOT"
make validate
```

## Prompt Templates

Shared between the Codex and Claude Code surfaces; edit in one place:

- `../../../../prompts/document-generator/tailored-system.md`
- `../../../../prompts/document-generator/tailored-task.md`
- `../../../../prompts/document-generator/archive-checklist.md`

## Promotion Workflow

Promotion is checklist-only by default. Do not copy content from a private run
into this public repo unless Brandon explicitly approves the specific sanitized
files to publish.

1. Read `docs/ARCHIVE_CONTRACT.md`.
2. Confirm the run is eligible for `sanitized-public-example` publication.
3. Remove or summarize third-party job description text.
4. Remove recruiter or company contact details unless already public.
5. Limit Brandon's contact details to the same public fields already in
   `output/`.
6. Review prompts and notes for private strategy or sensitive reasoning.
7. Produce a diff plan listing proposed public files and redactions.
8. After Brandon approves the public example, apply the sanitized changes and run:

```bash
make validate
make test
make privacy-scan
```
