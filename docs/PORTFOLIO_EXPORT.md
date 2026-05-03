# Portfolio Export

The portfolio site should consume stable static files from this repo rather than
parse YAML directly.

## Export Command

```bash
make export
```

This writes:

- `exports/profile.json`: normalized profile, public document metadata, source
  repository metadata, document sections, PDF paths, and preview paths.

Render PDF preview images with:

```bash
make showcase
```

`docs/showcase/*` contains preview and social assets intended for GitHub and
future site display.

## Site Integration Contract

The portfolio repo should treat `exports/profile.json` as read-only build input.
It can copy or fetch:

- `output/resume.pdf`
- `output/cv.pdf`
- `output/leadership_resume.pdf`
- `output/coverletter.pdf`
- `docs/showcase/*.png` or `.svg`

The portfolio should not edit `content/` directly. Official document changes
start here, pass validation, rebuild PDFs, then update the export bundle.
