# Custom Generation Archive Contract

Custom document-generation runs are archived in a private companion repo. The
public `About-Me` repo documents the archive shape and tooling, but raw run
archives are not committed here.

## Default Archive Target

Set `CUSTOM_GENERATION_ARCHIVE_ROOT` to the private archive repo checkout before
running archive scripts:

```bash
export CUSTOM_GENERATION_ARCHIVE_ROOT=/path/to/private/about-me-generations
```

Recommended private repo name: `Brandon-Gottshall/about-me-generations`.
Brandon's local checkout is expected at
`$HOME/Documents/GitHub/about-me-generations`.

The private repo should provide its own setup and validation helpers. Current
expected commands there:

```bash
source scripts/env.sh
make validate
make doctor
```

## Run Directory Shape

```text
runs/
`-- YYYY/
    `-- YYYY-MM-DD-company-role-slug/
        |-- manifest.json
        |-- input/
        |   |-- job-description.md
        |   `-- source-notes.md
        |-- prompts/
        |   |-- system.md
        |   `-- task.md
        |-- selected-facts/
        |   `-- profile-facts.yaml
        |-- drafts/
        |   |-- resume.md
        |   |-- cover-letter.md
        |   `-- cv.md
        |-- artifacts/
        |   |-- resume.pdf
        |   |-- coverletter.pdf
        |   `-- generated-tex/
        `-- verification/
            |-- validation.txt
            |-- build.txt
            `-- privacy-scan.txt
```

## Manifest Requirements

Each `manifest.json` follows
`schemas/archive/custom-generation-run.schema.json` and records:

- run id, timestamps, target company, role, and source URL when available
- source commit from this public repo
- model/tool names and agent environment
- input paths and generated artifact paths
- selected source facts from `content/`
- validation, build, privacy, and final decision status
- publication state: `private`, `sanitized-public-example`, or `discarded`

## Promotion Rules

A run may be copied into a public sanitized example only after:

1. Third-party job description text is removed or summarized.
2. Recruiter/company contact details are removed unless already public.
3. Personal contact details are limited to the same public fields already in
   `output/`.
4. Prompts and notes are reviewed for private strategy or sensitive reasoning.
5. The public example clearly states that it is sanitized.
