# Document Generator

Use this skill when working on Brandon Gottshall's About-Me repository: official
resume/CV/cover-letter generation, portfolio exports, tailored document drafts,
or private provenance archives.

## Guardrails

- Treat `content/` as the source of truth. Do not invent facts, dates, metrics,
  credentials, or contact data.
- Preserve Awesome CV provenance. Do not claim whole-repo MIT while
  `src/awesome-cv.cls` remains.
- Keep raw job descriptions, recruiter messages, prompts, and tailored artifacts
  out of public git unless Brandon explicitly promotes a sanitized example.
- Do not inspect or transmit private archive contents unless Brandon explicitly
  approves that specific use.

## Official Build Workflow

```bash
make validate
make test
make all
make export
make privacy-scan
```

Use `python -m document_pipeline ...` for narrower runs:

```bash
python -m document_pipeline generate resume
python -m document_pipeline build cover-letter
python -m document_pipeline privacy-scan
```

## Tailored Draft Workflow

1. Read `AGENTS.md`, `PROVENANCE.md`, and `docs/ARCHIVE_CONTRACT.md`.
2. Use only facts already present in `content/`.
3. Record selected source facts and validation/build status.
4. Archive run provenance in the private companion repo configured by
   `CUSTOM_GENERATION_ARCHIVE_ROOT`.
5. Leave public git clean unless Brandon asks to promote official source edits
   or sanitized examples.

Shared prompt templates live at:

- `../../../prompts/document-generator/tailored-system.md`
- `../../../prompts/document-generator/tailored-task.md`
- `../../../prompts/document-generator/archive-checklist.md`

## Archive Helper

```bash
ARCHIVE_AGENT_TOOL=claude python plugins/document-generator/scripts/archive_generation.py \
  --company "Company" \
  --role "Role" \
  --source-url "https://example.com/job"
```
