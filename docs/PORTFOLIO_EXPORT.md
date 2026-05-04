# Portfolio Export

The portfolio site should consume stable static files from this repo rather than
parse YAML directly. `content/` remains the source of truth, and
`exports/profile.json` is the public integration boundary.

## Generate The Bundle

```bash
make export
make showcase
```

`make export` writes `exports/profile.json`. `make showcase` refreshes preview
images in `docs/showcase/`.

Run the full verification path before publishing profile-facing changes:

```bash
make verify
```

## Public Files

The portfolio repo may copy or fetch these files from the public GitHub repo:

- `exports/profile.json`
- `output/resume.pdf`
- `output/cv.pdf`
- `output/leadership_resume.pdf`
- `output/coverletter.pdf`
- `docs/showcase/*.png`

`docs/showcase/social-preview.svg` is the editable design source for the GitHub
social card. Prefer the generated PNG for web display.

## JSON Contract

Top-level fields in `exports/profile.json`:

- `generatedAt`: UTC timestamp for the export.
- `source`: public repository URL and source directory metadata.
- `profile`: normalized profile data safe for portfolio display.
- `documents`: public PDF records with labels, paths, preview paths, page counts,
  and existence flags.
- `documentConfig`: official section order for resume, CV, and leadership resume.

Each document record includes both `path` and `publicPath`, plus both `preview`
and `previewPath`, so a consuming site can migrate without breaking older field
names. Treat `publicPath` and `previewPath` as the preferred names for new code.

## URL Resolution

The exported paths are repo-relative. A static site can resolve them in one of
two ways:

- Copy the files into the portfolio build and serve them from local public
  paths.
- Fetch them from the GitHub raw or release surface during the portfolio build.

Do not hotlink private archive artifacts. Job-specific tailoring runs belong in
the private companion archive and are not part of this public contract.

## Ownership Rules

The portfolio should treat `exports/profile.json` as read-only build input.
Official document changes start in this repo:

1. Update `content/` or `config/`.
2. Run `make validate`.
3. Run `make all` when PDFs need to change.
4. Run `make export` and `make showcase`.
5. Run `make privacy-scan` before publishing.

The portfolio should not edit `content/`, generated PDFs, preview images, or the
export JSON directly. It should consume the published outputs and present them.
