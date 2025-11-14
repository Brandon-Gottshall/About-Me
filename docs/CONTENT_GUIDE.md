# Content Guide

How to update and manage your CV/Resume content.

## Content Structure

### Core Content (`content/core/`)

**Required files** - These are used in all documents:

- **`personal.yaml`** - Your personal information
  - Name, contact details, address
  - Social media links
  - Professional quote/summary

- **`summary.yaml`** - Professional summary text
  - Used at the top of documents
  - 2-3 sentences describing your professional background

- **`experience.yaml`** - Work experience entries
  - List of jobs/positions
  - Each entry: title, organization, location, dates, responsibilities

- **`education.yaml`** - Education history
  - Degrees, certifications, courses
  - Institution, location, dates, details

- **`skills.yaml`** - Technical and professional skills
  - Technical skills: languages, frameworks, tools
  - Professional skills: leadership, communication, etc.

### Optional Content (`content/optional/`)

**Optional files** - Enable these in `config/documents.yaml`:

- **`certifications.yaml`** - Professional certifications
- **`projects.yaml`** - Notable projects
- **`languages.yaml`** - Language proficiencies
- **`publications.yaml`** - Research publications
- **`presentations.yaml`** - Conference presentations
- **`teaching.yaml`** - Teaching/mentoring experience
- **`volunteer.yaml`** - Volunteer work

## Editing Content

### Adding Work Experience

Edit `content/core/experience.yaml`:

```yaml
entries:
  - title: "Software Engineer"
    organization: "Company Name"
    location: "City, State"
    start_date: "Jan 2020"
    end_date: "Present"
    items:
      - "Led development of..."
      - "Improved performance by..."
```

### Adding Skills

Edit `content/core/skills.yaml`:

```yaml
technical:
  - category: "Languages"
    items: "TypeScript, JavaScript, Python"
  - category: "Frameworks"
    items: "React, Next.js, Node.js"

professional:
  - category: "Leadership"
    items: "Team Leadership, Mentoring"
```

### Enabling Optional Sections

Edit `config/documents.yaml`:

```yaml
cv:
  sections:
    - summary
    - experience
    - education
    - skills
    - certifications  # Add this line
    - projects        # Add this line
```

## Best Practices

1. **Keep entries current** - Update dates and remove outdated information
2. **Use action verbs** - Start bullet points with verbs (Led, Developed, Improved)
3. **Quantify impact** - Include metrics when possible (e.g., "Improved performance by 40%")
4. **Tailor for purpose** - Resume should be concise, CV can be comprehensive
5. **Keep it honest** - Only include accurate information

## File Format

All content files use YAML format:
- Use spaces for indentation (not tabs)
- Strings can be quoted or unquoted
- Lists use `-` prefix
- Nested structures use indentation

## Validation

After editing, test your changes:
```bash
make generate  # Check for YAML errors
make all       # Build to verify formatting
```

