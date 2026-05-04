# Agent Operating Guide

This repo is Brandon Gottshall's official document source of truth. Treat it as
career infrastructure, not a generic LaTeX theme.

## Required Workflow

1. Read `PROVENANCE.md` before changing license, template, or output behavior.
2. Validate YAML before generation: `make validate`.
3. Generate through the documented pipeline only: `make generate`, `make all`,
   or `python -m document_pipeline generate`.
4. Run tests and privacy checks before committing: `make test` and
   `make privacy-scan`.
5. Render PDFs when layout changed. Use `pdftoppm` and inspect pages for
   overlap, clipped text, and blank pages.

## Content Rules

- `content/` is the source of truth for official profile facts.
- Do not invent experience, education, metrics, credentials, or contact data.
- Do not remove personal fields only because they are sensitive. Report privacy
  concerns and let Brandon decide.
- Public PDFs in `output/` intentionally include Brandon's professional contact
  details.
- Job-specific drafts and full provenance archives belong in the private
  companion archive repo, not this public repo.

## Agent-Specific Drafting Rules

- Tailored resumes, CVs, and cover letters must cite which source facts from
  `content/` were used.
- Every tailored run must preserve full provenance in the private archive:
  input job description, prompts, selected profile facts, generated artifacts,
  validation/build results, and final decision metadata.
- Public examples must be explicitly promoted and sanitized.
- Never commit raw job descriptions, recruiter emails, third-party contact
  details, or model reasoning traces to this public repo.

## Verification Commands

```bash
make validate
make test
make all
make export
make privacy-scan
```

GitHub Actions runs lightweight validation, tests, LaTeX generation, export, and
privacy scans on pushes and pull requests. Full PDF smoke builds are limited to
pushes on `master` and manual workflow runs because XeLaTeX setup is heavier and
PDF byte output can vary between environments.
