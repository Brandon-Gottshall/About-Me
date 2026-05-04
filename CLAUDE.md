# Claude Code Guardrails

This is Brandon Gottshall's official document source of truth — career
infrastructure, not a generic LaTeX theme.

## Hard rules

- `content/` is the only source of truth for official profile facts. Do not
  invent experience, education, metrics, credentials, or contact data.
- Do not commit raw job descriptions, recruiter emails, third-party contact
  details, or model reasoning traces to this public repo. Job-specific drafts
  and full provenance archives belong in the private companion archive repo
  configured by `CUSTOM_GENERATION_ARCHIVE_ROOT`.
- Do not claim whole-repo MIT. The `src/awesome-cv.cls` lineage is LPPL v1.3c.
  See `PROVENANCE.md` before touching license, template, or output behavior.
- Personal fields in `content/` are intentionally public. Report privacy
  concerns and let Brandon decide rather than removing fields unilaterally.

## Verification commands

```bash
make validate
make test
make all
make export
make privacy-scan
```

Run these before proposing changes that touch source data, templates, or the
pipeline.

## Workflow

The `document-generator` skill (under `.claude/skills/`) covers the official
build, tailored-draft, and private-archive workflows. The
`/validate`, `/build-official`, `/tailored-draft`, `/archive-run`, and
`/promote-example` slash commands are the discoverable entry points. Read `AGENTS.md`,
`docs/ARCHIVE_CONTRACT.md`, and `PROVENANCE.md` before larger edits.
