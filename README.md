# Brandon Gottshall Document Pipeline

YAML-driven resume, CV, leadership resume, and cover-letter generator for Brandon Gottshall's portfolio documents.

## Generated Documents

PDF:

- [Resume](output/resume.pdf)
- [CV](output/cv.pdf)
- [Leadership resume](output/leadership_resume.pdf)
- [Cover letter](output/coverletter.pdf)

HTML:

- [Resume HTML](output/resume.html)
- [CV HTML](output/cv.html)
- [Leadership resume HTML](output/leadership_resume.html)
- [Cover letter HTML](output/coverletter.html)

Manifest:

- [Public documents manifest](output/documents.json)

The active cover-letter variant is configured in [config/documents.yaml](config/documents.yaml). The current checked-in configuration generates the Blazin' Brigade academic music leadership letter.

## What The Generator Supports

- PDF output through XeLaTeX and the local Awesome CV class.
- HTML output with inline CSS for portfolio-friendly linking.
- Resume, CV, leadership resume, and cover-letter document types.
- Cover-letter variants from `config/cover_letters/*.yaml` and `content/cover_letters/variants/*/paragraphs.yaml`.
- Section selection through `config/documents.yaml`.
- A public `output/documents.json` manifest for portfolio integration. The manifest intentionally exposes only the resume and CV.
- GitHub Pages publishing from `output/` after the full verification path passes on `master`.

## Prerequisites

- Python 3.7+
- XeLaTeX
- Python packages from [requirements.txt](requirements.txt)

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Or run commands through `uv` without creating a repo-local virtualenv:

```bash
make PYTHON='uv run --with PyYAML --with Jinja2 python' all html
```

## Common Commands

Generate LaTeX:

```bash
make generate
python3 scripts/generate.py
```

Build all PDFs:

```bash
make all
```

Build all HTML files:

```bash
make html
```

Build one document:

```bash
python3 scripts/build.py resume
python3 scripts/build.py cv
python3 scripts/build.py cover-letter
python3 scripts/build.py leadership-resume
```

Generate one HTML document:

```bash
python3 scripts/build.py --html resume
```

Run regression checks:

```bash
make test
make validate-yaml
```

Run the full local verification path:

```bash
make verify
```

## Project Structure

```text
content/core/                    Required personal, summary, experience, education, and skills data
content/optional/                Optional sections such as certifications, projects, languages, leadership
content/cover_letters/variants/  Cover-letter paragraph content by variant
config/documents.yaml            Document sections, settings, and active cover-letter variant
config/cover_letters/            Cover-letter variant metadata
templates/                       LaTeX templates
templates/html/                  HTML templates and CSS
scripts/generate.py              Thin compatibility entrypoint
scripts/document_generator/      Generator package split by responsibility
scripts/build.py                 Generation and XeLaTeX build wrapper
generated/                       Generated LaTeX files, ignored by git
output/                          Generated PDFs and HTML files
```

The package modules have narrow jobs:

- `content.py` loads YAML and names supported documents.
- `text.py` escapes shared LaTeX and HTML text.
- `entries.py` formats resume/CV entries and skills.
- `cover_letters.py` loads cover-letter variants and paragraphs.
- `latex.py` renders LaTeX sections and documents.
- `html.py` renders HTML sections and documents.
- `manifest.py` writes the public document manifest.
- `cli.py` connects the command line to the renderers.

## Portfolio Publishing Contract

The portfolio should consume the GitHub Pages output from this repo rather than raw GitHub files. Public portfolio links come from `output/documents.json`, which lists the resume and CV with relative PDF and HTML paths.

GitHub Pages is configured by [.github/workflows/publish-documents.yml](.github/workflows/publish-documents.yml). The workflow installs Python and TeX dependencies, runs `make verify`, and publishes the `output/` directory only after verification succeeds.

## Editing Content

Core profile content lives in `content/core/`. Optional sections can stay empty; the generator skips empty optional sections instead of producing blank headings.

Cover-letter variants are split between metadata and paragraph content:

- Variant metadata: `config/cover_letters/<variant>.yaml`
- Paragraphs: `content/cover_letters/variants/<variant>/paragraphs.yaml`

After editing content or templates, rebuild and verify:

```bash
make verify
```

## Acknowledgements

This project uses the [Awesome CV](https://github.com/posquit0/Awesome-CV) LaTeX template by Claud D. Park, licensed under the [LaTeX Project Public License v1.3c](LICENCE).
