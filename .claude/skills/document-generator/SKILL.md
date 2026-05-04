---
name: document-generator
description: Use for Brandon Gottshall's About-Me repo when validating YAML, generating official PDFs, exporting portfolio data, drafting tailored resume/CV/cover-letter variants, or archiving custom generation runs with private provenance.
---

# Document Generator

Use this skill when working on Brandon Gottshall's About-Me repository: official
resume/CV/cover-letter generation, portfolio exports, tailored document drafts,
or private provenance archives.

Unless explicitly stated otherwise, file paths below are repo-relative.

## Repo Contract

- Treat `content/` as the source of truth. Do not invent facts, dates, metrics,
  credentials, or contact data.
- Validate before generating: `make validate`.
- Rebuild official public outputs with `make all`.
- Refresh portfolio data with `make export`.
- Run `make privacy-scan` before committing or publishing.
- Preserve Awesome CV provenance. Do not claim whole-repo MIT while
  `src/awesome-cv.cls` remains.
- Keep raw job descriptions, recruiter messages, prompts, and tailored artifacts
  out of public git unless Brandon explicitly promotes a sanitized example.
- Do not inspect or transmit private archive contents unless Brandon explicitly
  approves that specific use.

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

4. If layout or PDFs changed, render pages with `pdftoppm` and inspect for
   overlap, clipped text, and blank pages.

Use `python -m document_pipeline ...` for narrower runs and agent automation:

```bash
python -m document_pipeline generate resume
python -m document_pipeline generate cv
python -m document_pipeline generate cover-letter
python -m document_pipeline generate leadership-resume
python -m document_pipeline build cover-letter
python -m document_pipeline export
python -m document_pipeline privacy-scan
```

## Tailored Draft Workflow

1. Read `AGENTS.md`, `PROVENANCE.md`, and `docs/ARCHIVE_CONTRACT.md`.
2. Use only facts already present in `content/`.
3. Cite selected facts as `content/<file>.yaml:<key>` or a more precise dotted
   key when needed.
4. Archive run provenance in the private companion repo configured by
   `CUSTOM_GENERATION_ARCHIVE_ROOT`.
5. If an artifact should become official, promote the source edits into
   `content/` and rebuild official PDFs.
6. If an artifact should become a public example, sanitize it according to
   `docs/ARCHIVE_CONTRACT.md`.
7. Leave public git clean unless Brandon asks to promote official source edits
   or sanitized examples.

Shared prompt templates live at:

- `prompts/document-generator/tailored-system.md`
- `prompts/document-generator/tailored-task.md`
- `prompts/document-generator/archive-checklist.md`

## Archive Helper

Use the helper only after setting a private archive root:

```bash
source "$HOME/Documents/GitHub/about-me-generations/scripts/env.sh"
```

If that helper is unavailable, set the root explicitly:

```bash
export CUSTOM_GENERATION_ARCHIVE_ROOT="$HOME/Documents/GitHub/about-me-generations"
```

```bash
ARCHIVE_AGENT_TOOL=claude python plugins/document-generator/scripts/archive_generation.py \
  --company "Company" \
  --role "Role" \
  --source-url "https://example.com/job"
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
