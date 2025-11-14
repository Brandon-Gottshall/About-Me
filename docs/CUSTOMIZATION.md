# Customization Guide

How to customize templates and styling.

## Template Structure

Templates are in `templates/`:
- **Base templates**: `base_resume.tex`, `base_cv.tex`, `base_cover_letter.tex`
- **Section templates**: `templates/sections/*.tex`

## Document Configuration

Edit `config/documents.yaml` to control:

### Which Sections Appear

```yaml
resume:
  sections:
    - summary
    - experience
    - education
    - skills
    - certifications

cv:
  sections:
    - summary
    - experience
    - education
    - skills
    - certifications
    - projects
    - publications
    - presentations
```

### Document Settings

```yaml
resume:
  settings:
    paper_size: "a4paper"      # or "letterpaper"
    font_size: "11pt"
    margins:
      left: "1.8cm"
      top: "1.5cm"
      right: "1.8cm"
      bottom: "2.2cm"
    color: "awesome-skyblue"    # Color scheme
    section_color_highlight: true
    header_alignment: "C"       # C=center, L=left, R=right
```

## Color Schemes

Available colors:
- `awesome-skyblue`
- `awesome-red`
- `awesome-emerald`
- `awesome-pink`
- `awesome-orange`
- `awesome-nephritis`
- `awesome-concrete`
- `awesome-darknight`

## Customizing Templates

### Modify Base Template

Edit `templates/base_resume.tex` (or `base_cv.tex`, `base_cover_letter.tex`):
- Change margins, fonts, spacing
- Modify header/footer
- Adjust layout

### Modify Section Template

Edit `templates/sections/*.tex`:
- Change section formatting
- Modify bullet point style
- Adjust spacing

**Note**: Templates use Jinja2 syntax with custom delimiters (`<<variable>>`). Don't modify the template variables unless you understand the generator code.

## Advanced Customization

### Custom LaTeX Commands

Add custom commands to base templates:

```latex
% In base_resume.tex
\newcommand{\mycustomcommand}[1]{\textbf{#1}}
```

### Custom Sections

1. Create new section template in `templates/sections/`
2. Add data file in `content/optional/`
3. Update generator script to handle new section
4. Add to `config/documents.yaml`

## Regenerating After Changes

After modifying templates:
```bash
make generate  # Regenerate LaTeX files
make all       # Rebuild PDFs
```

## Troubleshooting

**LaTeX errors**: Check `output/*.log` for compilation errors
**Missing sections**: Verify section is enabled in `config/documents.yaml`
**Formatting issues**: Check template syntax and LaTeX commands

