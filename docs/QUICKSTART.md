# Quick Start Guide

Get your CV/Resume/Cover Letter system up and running in minutes.

## Prerequisites

1. **Python 3.7+** - Check with `python3 --version`
2. **XeLaTeX** - Required for PDF compilation
3. **Python packages** - Install with `pip install -r requirements.txt`

## First Time Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Update your personal information**:
   - Edit `content/core/personal.yaml` - Your name, contact info, address
   - Edit `content/core/summary.yaml` - Your professional summary

3. **Add your experience**:
   - Edit `content/core/experience.yaml` - Your work history
   - Edit `content/core/education.yaml` - Your education
   - Edit `content/core/skills.yaml` - Your skills

4. **Configure documents** (optional):
   - Edit `config/documents.yaml` - Control which sections appear in resume vs CV

5. **Generate and build**:
   ```bash
   make all
   ```

6. **Find your PDFs**:
   - Resume: `output/resume.pdf`
   - CV: `output/cv.pdf`
   - Cover Letter: `output/coverletter.pdf`

## Common Workflows

### Update Your Resume
1. Edit files in `content/core/`
2. Run `make resume`

### Add Optional Sections
1. Add entries to files in `content/optional/`
2. Enable the section in `config/documents.yaml`
3. Run `make all`

### Customize Cover Letter
1. Edit `config/cover_letter.yaml`
2. Run `make cover-letter`

## Next Steps

- See [CONTENT_GUIDE.md](CONTENT_GUIDE.md) for detailed content editing
- See [CUSTOMIZATION.md](CUSTOMIZATION.md) for template customization

