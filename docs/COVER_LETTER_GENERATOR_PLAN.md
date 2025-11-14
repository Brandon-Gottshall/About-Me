# Cover Letter Generator Plan

## Overview

Design a flexible cover letter generation system that supports multiple variants (e.g., standard tech positions, academic music leadership positions) with structured, reusable paragraph components.

## Current State Analysis

### Existing Infrastructure
- ✅ Cover letter template (`templates/base_cover_letter.tex`)
- ✅ Basic cover letter config (`config/cover_letter.yaml`)
- ✅ Generation script support (`scripts/generate.py`)
- ✅ Build automation (`scripts/build.py`, `Makefile`)

### Current Limitations
- Single cover letter variant only
- Body content is one monolithic text block
- No paragraph structure or reusability
- No variant-specific content management
- Hard to maintain multiple letter types

## Proposed Architecture

### 1. Directory Structure

```
config/
  cover_letters/
    default.yaml              # Default/standard cover letter
    academic_music.yaml       # Academic Music Leadership variant
    [future_variant].yaml     # Additional variants as needed

content/
  cover_letters/
    paragraphs/
      introduction.yaml       # Reusable intro paragraphs
      experience.yaml         # Experience-focused paragraphs
      leadership.yaml         # Leadership-focused paragraphs
      closing.yaml            # Closing paragraphs
    variants/
      academic_music/
        paragraphs.yaml       # Variant-specific paragraph content
```

### 2. Data Structure Design

#### Variant Configuration (`config/cover_letters/[variant].yaml`)

```yaml
# Variant metadata
variant_name: "Academic Music Leadership"
variant_id: "academic_music"

# Letter-specific metadata
recipient_name: "Blazin' Brigade Leadership Selection Committee"
company_name: "Valdosta State University"
company_address: |
  Valdosta State University
  Valdosta, GA
position_name: "Section Leader"
letter_opening: "Dear Selection Committee,"
letter_closing: "Sincerely,"

# Paragraph structure - ordered list of paragraph references
paragraphs:
  - type: "introduction"
    source: "variant"  # or "shared" for reusable paragraphs
    content_id: "opening_positioning"
  
  - type: "experience"
    source: "variant"
    content_id: "leadership_toolkit"
  
  - type: "experience"
    source: "variant"
    content_id: "mentorship_philosophy"
  
  - type: "personal"
    source: "variant"
    content_id: "musicianship_rebuild"
  
  - type: "vision"
    source: "variant"
    content_id: "leadership_vision"
  
  - type: "closing"
    source: "shared"
    content_id: "standard_closing"
```

#### Paragraph Content (`content/cover_letters/variants/academic_music/paragraphs.yaml`)

```yaml
paragraphs:
  opening_positioning:
    text: |
      Leading from the front defines my approach to leadership. I am applying 
      for the Section Leader position with the Blazin' Brigade because this 
      role aligns with my strengths: disciplined leadership, musical excellence, 
      and building strong, cohesive teams. As a Marine Corps veteran, Accredited 
      Technology Instructor, and former low brass section leader, I know that 
      clear expectations and shared accountability are the foundation of any 
      successful ensemble.
  
  leadership_toolkit:
    text: |
      My leadership toolkit was shaped by my service in the Marine Corps, where 
      I held the roles of Quality Control NCO and Assistant Maintenance Chief...
  
  mentorship_philosophy:
    text: |
      Mentorship drives me. As an Accredited Technology Instructor, I developed 
      project-based curricula that turned beginners into confident practitioners...
  
  musicianship_rebuild:
    text: |
      After several years focused on service and career, I have rebuilt my 
      musicianship intensively since August...
  
  leadership_vision:
    text: |
      My vision for leadership is to strengthen the internal support structure 
      of the section...
```

#### Shared Paragraphs (`content/cover_letters/paragraphs/[category].yaml`)

```yaml
# content/cover_letters/paragraphs/closing.yaml
paragraphs:
  standard_closing:
    text: |
      Thank you for considering my application. I am eager to collaborate 
      with the leadership team and staff to support the ensemble's goals...
  
  tech_closing:
    text: |
      Thank you for considering my application. I would welcome the opportunity 
      to discuss how my background, skills, and enthusiasm align with the needs 
      of [Company Name]...
```

### 3. Generator Logic Flow

```
1. Load variant config (config/cover_letters/[variant].yaml)
2. For each paragraph in paragraph list:
   a. Determine source (variant-specific or shared)
   b. Load paragraph content from appropriate file
   c. Apply any variable substitutions (e.g., [Company Name])
   d. Escape LaTeX special characters
   e. Format as LaTeX paragraph with proper spacing
3. Combine paragraphs into letter body
4. Render template with all metadata + formatted body
```

### 4. Implementation Details

#### Enhanced `generate.py` Functions

```python
def load_cover_letter_variant(variant_id, config_dir, content_dir):
    """Load a specific cover letter variant configuration."""
    variant_config_path = config_dir / 'cover_letters' / f'{variant_id}.yaml'
    variant_config = load_yaml(variant_config_path)
    
    # Load paragraph content
    paragraphs = []
    for para_ref in variant_config['paragraphs']:
        if para_ref['source'] == 'variant':
            para_content = load_variant_paragraph(
                variant_id, para_ref['content_id'], content_dir
            )
        else:  # shared
            para_content = load_shared_paragraph(
                para_ref['type'], para_ref['content_id'], content_dir
            )
        paragraphs.append(para_content)
    
    return variant_config, paragraphs

def format_cover_letter_body(paragraphs, substitutions=None):
    """Format paragraphs into LaTeX body with proper spacing."""
    formatted_paragraphs = []
    for para in paragraphs:
        text = para['text']
        # Apply substitutions
        if substitutions:
            for key, value in substitutions.items():
                text = text.replace(f'[{key}]', value)
        # Escape LaTeX and format
        escaped = escape_latex(text)
        formatted_paragraphs.append(escaped)
    
    # Join with double newline for paragraph breaks
    return '\n\n'.join(formatted_paragraphs)
```

#### Command-Line Interface

```bash
# Generate default cover letter
python scripts/generate.py cover-letter

# Generate specific variant
python scripts/generate.py cover-letter --variant academic_music

# Or via Makefile
make cover-letter VARIANT=academic_music
```

### 5. Template Updates

The existing `base_cover_letter.tex` template should work with minimal changes - it already accepts `letter_body` as a variable. The generator will format the body with proper paragraph breaks.

### 6. Benefits

1. **Maintainability**: Each variant is self-contained
2. **Reusability**: Shared paragraphs can be used across variants
3. **Flexibility**: Easy to add new variants or modify existing ones
4. **Structure**: Clear paragraph organization makes editing easier
5. **Consistency**: Shared components ensure consistent tone/style

### 7. Migration Path

1. Create new directory structure (`config/cover_letters/`, `content/cover_letters/`)
2. Extract current `cover_letter.yaml` content into `default.yaml` variant
3. Create `academic_music.yaml` variant with structured paragraphs
4. Update `generate.py` to support variant loading
5. Update `build.py` and `Makefile` to accept variant parameter
6. Test with both variants

### 8. Future Enhancements

- Paragraph templates with placeholders
- Variable substitution system (e.g., `{company_name}`, `{position_name}`)
- Paragraph library/search system
- A/B testing different paragraph combinations
- Export to different formats (Word, PDF directly)

## Implementation Checklist

- [ ] Create directory structure
- [ ] Design YAML schema for variants and paragraphs
- [ ] Implement variant loading functions
- [ ] Implement paragraph formatting functions
- [ ] Update `generate_document()` for cover letters
- [ ] Add variant parameter to CLI
- [ ] Update `build.py` to handle variants
- [ ] Update `Makefile` targets
- [ ] Create `default.yaml` variant (migrate existing)
- [ ] Create `academic_music.yaml` variant
- [ ] Create paragraph content files
- [ ] Test generation and compilation
- [ ] Update documentation

