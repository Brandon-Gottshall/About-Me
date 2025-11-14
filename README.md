# Brandon Gottshall

> Software Engineer & Technology Enthusiast

[![Email](https://img.shields.io/badge/Email-blgottshall%40gmail.com-blue?style=flat-square&logo=gmail)](mailto:blgottshall@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/brandon-gottshall)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat-square&logo=github&logoColor=white)](https://github.com/Brandon-Gottshall)

## 👋 About Me

I'm a passionate software engineer with expertise in full-stack development, cloud architecture, and building scalable applications. I love solving complex problems and continuously learning new technologies to stay at the forefront of the industry.

### 📋 Table of Contents

- [About Me](#-about-me)
- [Technical Skills](#️-technical-skills)
- [Currently Learning](#-currently-learning)
- [Projects](#-projects)
- [Get In Touch](#-get-in-touch)
- [GitHub Stats](#-github-stats)
- [CV/Resume Generator System](#cvresume-generator-system)

## 🔍 Currently Learning

- Advanced TypeScript patterns
- Cloud architecture best practices
- Performance optimization techniques

### 🛠️ Technical Skills

- **Languages**: TypeScript, JavaScript, Python, Java, SQL
- **Frontend**: React, Next.js, Redux, HTML5, CSS3, Tailwind CSS
- **Backend**: Node.js, Express, NestJS, Django, Spring Boot
- **Cloud & DevOps**: AWS, GCP, Docker, Kubernetes, Terraform, CI/CD
- **Databases**: PostgreSQL, MongoDB, Redis, DynamoDB
- **Other**: GraphQL, REST APIs, Microservices, Serverless

### 📄 Professional Documents

- [Resume](output/resume.pdf)
- [CV](output/cv.pdf)
- [Cover Letter Template](output/coverletter.pdf)

## 📄 Résumé Preview

| Page. 1 | Page. 2 |
|:---:|:---:|
| *Resume preview images will be generated after building* | *Resume preview images will be generated after building* |

## 📄 CV Preview

| Page. 1 | Page. 2 |
|:---:|:---:|
| *CV preview images will be generated after building* | *CV preview images will be generated after building* |

### Cover Letter Preview

| Without Sections | With Sections |
|:---:|:---:|
| *Cover letter preview images will be generated after building* | *Cover letter preview images will be generated after building* |

## 🚀 Projects

Here are some of my notable projects:

- **Project One** - Brief description of the project and your role.
- **Project Two** - Brief description of the project and technologies used.
- **Project Three** - Brief description of the impact or results.

## 📫 Get In Touch

- 📧 [blgottshall@gmail.com](mailto:blgottshall@gmail.com)
- 💼 [LinkedIn](https://linkedin.com/in/brandon-gottshall)
- 🐦 [Twitter](https://twitter.com/yourhandle)
- 🌐 [Website](https://yourwebsite.com)

## 📊 GitHub Stats

[![Brandon's GitHub Stats](https://github-readme-stats.vercel.app/api?username=Brandon-Gottshall&show_icons=true&theme=radical&rank_icon=github)](https://github.com/Brandon-Gottshall)

> Disclaimer: These stats are currently generated based only on the **public** repositories of my GitHub profile. I plan to deploy my own instance of the GitHub Readme Stats API in the near future, however I can't be bothered at this very moment. 🤷‍♂️

## CV/Resume Generator System

This repository uses a data-driven generator system to create professional CV, Resume, and Cover Letter documents from centralized YAML data sources.

### Features

- **Single Source of Truth**: All personal information, experience, education, and skills are stored in YAML files
- **Automated Generation**: Python scripts generate LaTeX files from templates and data
- **Configurable Sections**: Enable/disable sections per document type via configuration
- **Easy Updates**: Update your information in YAML files, regenerate, and rebuild

### Project Structure

```
about-me/
├── content/                       # CONTENT: Your personal/professional data
│   ├── core/                      # REQUIRED: Core content for all documents
│   │   ├── personal.yaml          # Name, contact, address
│   │   ├── summary.yaml           # Professional summary
│   │   ├── experience.yaml        # Work experience
│   │   ├── education.yaml         # Education history
│   │   └── skills.yaml            # Technical and professional skills
│   └── optional/                   # OPTIONAL: Additional sections
│       ├── certifications.yaml    # Certifications
│       ├── projects.yaml          # Projects
│       ├── languages.yaml         # Languages
│       └── ...                    # Publications, presentations, etc.
│
├── config/                        # CONFIGURATION: Document settings
│   ├── documents.yaml             # Which sections appear in resume vs CV
│   └── cover_letter.yaml          # Cover letter defaults
│
├── templates/                     # TEMPLATES: LaTeX document templates
│   ├── base_resume.tex            # Resume base template
│   ├── base_cv.tex                # CV base template
│   ├── base_cover_letter.tex      # Cover letter base template
│   └── sections/                  # Section templates
│
├── generated/                     # GENERATED: Auto-generated LaTeX (gitignored)
│   ├── resume.tex
│   ├── cv.tex
│   └── coverletter.tex
│
├── output/                        # OUTPUT: Final PDFs and build artifacts
│   ├── resume.pdf
│   ├── cv.pdf
│   └── coverletter.pdf
│
├── src/                           # SOURCE: LaTeX class file
│   └── awesome-cv.cls
│
├── scripts/                       # TOOLS: Generation and build scripts
│   ├── generate.py
│   └── build.py
│
└── docs/                          # DOCUMENTATION: Guides and examples
    ├── QUICKSTART.md              # Quick start guide
    ├── CONTENT_GUIDE.md           # How to update content
    └── CUSTOMIZATION.md           # How to customize templates
```

### Prerequisites

- Python 3.7+
- XeLaTeX (for PDF compilation)
- Python packages: `PyYAML`, `Jinja2`

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Usage

#### Generate LaTeX files from data

```bash
# Generate all documents
make generate
# or
python3 scripts/generate.py

# Generate specific document
python3 scripts/generate.py resume
python3 scripts/generate.py cv
python3 scripts/generate.py cover-letter
```

#### Build PDFs

```bash
# Build all documents
make all

# Build specific document
make resume
make cv
make cover-letter

# Or use the build script directly
python3 scripts/build.py resume
python3 scripts/build.py cv
python3 scripts/build.py cover-letter
```

#### Clean build artifacts

```bash
make clean
```

### Quick Start

1. **Read the guide**: Start with [`docs/QUICKSTART.md`](docs/QUICKSTART.md)
2. **Update content**: Edit files in `content/core/`
3. **Configure**: Edit `config/documents.yaml` if needed
4. **Generate**: Run `make all`

### Updating Your Information

**Core Content** (required):
- `content/core/personal.yaml` - Personal information
- `content/core/experience.yaml` - Work experience
- `content/core/education.yaml` - Education history
- `content/core/skills.yaml` - Skills
- `content/core/summary.yaml` - Professional summary

**Optional Content**:
- `content/optional/certifications.yaml` - Certifications
- `content/optional/projects.yaml` - Projects
- `content/optional/languages.yaml` - Languages
- And more in `content/optional/`

**Configuration**:
- `config/documents.yaml` - Control which sections appear in resume vs CV
- `config/cover_letter.yaml` - Cover letter defaults

After making changes:
```bash
make all  # Regenerates and rebuilds all documents
```

### Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in minutes
- **[Content Guide](docs/CONTENT_GUIDE.md)** - How to update your content
- **[Customization Guide](docs/CUSTOMIZATION.md)** - How to customize templates

### Adding New Sections

1. Add data to `content/optional/` (or create a new YAML file)
2. Create a template in `templates/sections/`
3. Update `config/documents.yaml` to include the section
4. Update `scripts/generate.py` to handle the new section type

## 🙏 Acknowledgements

This project uses the [Awesome CV](https://github.com/posquit0/Awesome-CV) template created by [Claud D. Park](http://www.posquit0.com), which is licensed under the [LaTeX Project Public License (LPPL) v1.3c](LICENCE).

## 📜 License

- The LaTeX template files are licensed under the [LaTeX Project Public License (LPPL) v1.3c](LICENCE).
- The content of the CV/Resume and other personal files are licensed under the [MIT License](LICENSE).
