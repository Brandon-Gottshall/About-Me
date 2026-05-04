# Brandon Gottshall About-Me

YAML-driven LaTeX document-generation system for Brandon Gottshall's resume, CV,
leadership resume, and cover letters.

This repository began as a fork of
[posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV), but it has been
reworked into personal career infrastructure: structured YAML content feeds
document-specific LaTeX templates, Python scripts generate `.tex` files, and
XeLaTeX builds polished PDFs. It is also agent-ready: schemas, docs, a
repo-local Codex plugin, and Claude Code commands define how LLMs should
validate, generate, export, and privately archive tailored document runs.

## Current Outputs

- [Resume](output/resume.pdf)
- [CV](output/cv.pdf)
- [Leadership resume](output/leadership_resume.pdf)
- [Cover letter](output/coverletter.pdf)

These PDFs are public portfolio artifacts and include the professional contact
details stored in `content/core/personal.yaml`.

## Pipeline

| Layer | Paths | Purpose |
| --- | --- | --- |
| Source data | `content/core/`, `content/optional/`, `content/cover_letters/` | Canonical personal, professional, optional-section, and cover-letter text in YAML. |
| Document configuration | `config/documents.yaml`, `config/cover_letters/` | Selects sections, margins, colors, cover-letter variants, and document defaults. |
| LaTeX templates | `templates/`, `templates/sections/`, `src/awesome-cv.cls` | Defines the visual system and section-level rendering on top of Awesome CV. |
| Pipeline package | `document_pipeline/` | Typed content loading, YAML validation, LaTeX rendering, PDF builds, privacy scans, and portfolio export. |
| CLI surfaces | `python -m document_pipeline`, `scripts/`, `Makefile` | Stable commands for humans, agents, and future site automation. |
| Agent workflow | `AGENTS.md`, `plugins/document-generator/`, `.claude/` | Codex and Claude workflow rules and prompts for official and tailored documents. |

```text
YAML content + config
        |
        v
Python generator -> generated/*.tex
        |
        v
XeLaTeX builder -> output/*.pdf
```

## Quick Commands

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Generate LaTeX files from YAML:

```bash
make generate
```

The package CLI exposes the same pipeline directly:

```bash
python3 -m document_pipeline generate
python3 -m document_pipeline build resume
python3 -m document_pipeline validate
```

Validate content and configuration:

```bash
make validate
```

Generate and build every configured PDF:

```bash
make all
```

Build one document:

```bash
make resume
make cv
make cover-letter
make leadership-resume
```

Clean generated LaTeX and PDF build artifacts:

```bash
make clean
```

PDF compilation requires XeLaTeX. `make generate` only needs Python plus the
packages in `requirements.txt`.

Export portfolio data and run local verification:

```bash
make export
make showcase
make test
make privacy-scan
make verify
```

## Repository Structure

```text
.
|-- content/
|   |-- core/                  # Personal data, summary, experience, education, skills
|   |-- optional/              # Certifications, projects, publications, teaching, and more
|   `-- cover_letters/         # Cover-letter paragraph content by variant
|-- config/
|   |-- documents.yaml         # Document section lists and layout settings
|   |-- cover_letter.yaml      # Legacy cover-letter fallback defaults
|   `-- cover_letters/         # Variant-specific cover-letter metadata
|-- templates/
|   |-- base_resume.tex
|   |-- base_cv.tex
|   |-- base_cover_letter.tex
|   `-- sections/              # Reusable section templates
|-- scripts/
|   |-- generate.py            # YAML/template to LaTeX generation
|   `-- build.py               # XeLaTeX build orchestration
|-- document_pipeline/         # Typed loading, rendering, validation, build, export, and CLI modules
|-- schemas/                   # JSON Schemas for content, config, and archive manifests
|-- plugins/document-generator/# Repo-local Codex plugin and prompt templates
|-- exports/                   # Portfolio-ready static data
|-- generated/                 # Ignored generated .tex files
|-- output/                    # Tracked generated PDFs
|-- docs/                      # Editing and customization guides
|-- src/awesome-cv.cls         # Awesome CV LaTeX class
`-- Makefile                   # Common generation/build targets
```

## Document Types

- `resume`: concise job-application resume using core content and selected
  certifications.
- `cv`: broader professional profile. It currently includes populated optional
  sections such as certifications, languages, and references; additional
  optional sections remain available through `content/optional/` and
  `config/documents.yaml`.
- `leadership_resume`: alternate resume profile focused on leadership and
  ensemble experience.
- `cover-letter`: variant-driven cover letter assembled from configured
  paragraphs and recipient metadata.

## Editing Workflow

1. Update source content in `content/core/` and `content/optional/`.
2. Adjust section order, margins, colors, or cover-letter variants in `config/`.
3. Run `make validate` before generation.
4. Run `make generate` to inspect generated LaTeX when changing content or
   templates.
5. Run `make all` or a document-specific target to refresh PDFs in `output/`.
6. Run `make export` when public outputs change.

The generator accepts both hyphenated and underscored document names:

```bash
python3 -m document_pipeline generate resume
python3 -m document_pipeline generate cv
python3 -m document_pipeline generate cover-letter
python3 -m document_pipeline generate leadership-resume
```

## Documentation

- [Quick Start](docs/QUICKSTART.md)
- [Content Guide](docs/CONTENT_GUIDE.md)
- [Customization Guide](docs/CUSTOMIZATION.md)
- [Portfolio Export](docs/PORTFOLIO_EXPORT.md)
- [Custom Generation Archive Contract](docs/ARCHIVE_CONTRACT.md)
- [Cover Letter Generator Plan](docs/COVER_LETTER_GENERATOR_PLAN.md)

## Agent Workflows

Agents should start with [AGENTS.md](AGENTS.md). The repo-local Codex plugin in
`plugins/document-generator/` and the Claude Code surface in `.claude/` provide
workflow instructions, prompt templates, and an archive helper for private
job-specific generation runs.

Raw tailored runs belong in a private companion archive repo configured through
`CUSTOM_GENERATION_ARCHIVE_ROOT`. This public repo contains only the archive
contract, schema, and sanitized example structure.

## Portfolio Integration

`make export` writes `exports/profile.json`, which is the intended static input
for Brandon's portfolio site. The export includes normalized profile data,
public document metadata, PDF paths, and showcase preview paths without requiring
the site to parse YAML directly. See [Portfolio Export](docs/PORTFOLIO_EXPORT.md)
for the integration contract and ownership rules.

## Provenance

This repo was forked from
[Awesome CV](https://github.com/posquit0/Awesome-CV) by Claud D. Park. The
Awesome CV LaTeX class and template lineage remain credited here, while this fork
adapts the template into a data-driven personal document system for Brandon's
career materials.

The original Awesome CV template assets are distributed under the
[LaTeX Project Public License v1.3c](LICENCE). Brandon-authored tooling and docs
are covered by [LICENSE](LICENSE) as described in [PROVENANCE.md](PROVENANCE.md).
Brandon's YAML content and generated personal documents are portfolio material,
not a generic resume theme or reusable sample identity.
