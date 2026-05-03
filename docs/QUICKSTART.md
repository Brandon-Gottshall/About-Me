# Quick Start Guide

Get Brandon's YAML-driven resume, CV, leadership resume, and cover-letter
pipeline running locally.

## Prerequisites

1. **Python 3.10+** - Check with `python3 --version`
2. **XeLaTeX** - Required for PDF compilation
3. **Python packages** - Install with `pip install -r requirements.txt`

## First Time Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Review official profile data**:
   - Edit `content/core/personal.yaml` for contact/header data
   - Edit `content/core/summary.yaml` for profile summaries

3. **Update source-of-truth content**:
   - Edit `content/core/experience.yaml`
   - Edit `content/core/education.yaml`
   - Edit `content/core/skills.yaml`

4. **Configure documents** (optional):
   - Edit `config/documents.yaml` - Control which sections appear in resume vs CV

5. **Generate and build**:
   ```bash
   make all
   ```

6. **Find your PDFs**:
   - Resume: `output/resume.pdf`
   - CV: `output/cv.pdf`
   - Leadership resume: `output/leadership_resume.pdf`
   - Cover Letter: `output/coverletter.pdf`

The package CLI is available when a Makefile target is too coarse:

```bash
python3 -m document_pipeline validate
python3 -m document_pipeline generate resume
python3 -m document_pipeline build cover-letter
```

## Common Workflows

### Update Your Resume
1. Edit files in `content/core/`
2. Run `make resume`

### Add Optional Sections
1. Add entries to files in `content/optional/`
2. Enable the section in `config/documents.yaml`
3. Run `make all`

### Customize Cover Letter
1. Edit `config/cover_letters/<variant>.yaml`
2. Edit paragraph content in `content/cover_letters/variants/<variant>/`
3. Select the variant in `config/documents.yaml`
4. Run `make cover-letter`

## Next Steps

- See [CONTENT_GUIDE.md](CONTENT_GUIDE.md) for detailed content editing
- See [CUSTOMIZATION.md](CUSTOMIZATION.md) for template customization
