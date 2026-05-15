.PHONY: all resume cv cover-letter leadership-resume clean generate html html-resume html-cv html-cover-letter html-leadership-resume test syntax validate-yaml verify

# Python interpreter
PYTHON = python3

# Directories
SCRIPTS_DIR = scripts
GENERATED_DIR = generated
OUTPUT_DIR = output

# Generated LaTeX files
RESUME_TEX = $(GENERATED_DIR)/resume.tex
CV_TEX = $(GENERATED_DIR)/cv.tex
COVER_LETTER_TEX = $(GENERATED_DIR)/coverletter.tex
LEADERSHIP_RESUME_TEX = $(GENERATED_DIR)/leadership_resume.tex

# Output PDFs
RESUME_PDF = $(OUTPUT_DIR)/resume.pdf
CV_PDF = $(OUTPUT_DIR)/cv.pdf
COVER_LETTER_PDF = $(OUTPUT_DIR)/coverletter.pdf
LEADERSHIP_RESUME_PDF = $(OUTPUT_DIR)/leadership_resume.pdf

# Ensure directories exist
$(shell mkdir -p $(OUTPUT_DIR) $(GENERATED_DIR))

# Default target - build all documents
all: resume cv cover-letter leadership-resume

# Generate LaTeX files from YAML data
generate:
	$(PYTHON) $(SCRIPTS_DIR)/generate.py

# Build resume
resume: generate $(RESUME_PDF)

# Build CV
cv: generate $(CV_PDF)

# Build cover letter
cover-letter: generate $(COVER_LETTER_PDF)

# Build leadership resume
leadership-resume: generate $(LEADERSHIP_RESUME_PDF)

# Build resume PDF
$(RESUME_PDF): $(RESUME_TEX)
	$(PYTHON) $(SCRIPTS_DIR)/build.py resume

# Build CV PDF
$(CV_PDF): $(CV_TEX)
	$(PYTHON) $(SCRIPTS_DIR)/build.py cv

# Build cover letter PDF
$(COVER_LETTER_PDF): $(COVER_LETTER_TEX)
	$(PYTHON) $(SCRIPTS_DIR)/build.py cover-letter

# Build leadership resume PDF
$(LEADERSHIP_RESUME_PDF): $(LEADERSHIP_RESUME_TEX)
	$(PYTHON) $(SCRIPTS_DIR)/build.py leadership-resume

# Generate HTML files
html: html-resume html-cv html-cover-letter html-leadership-resume

html-resume:
	$(PYTHON) $(SCRIPTS_DIR)/build.py --html resume

html-cv:
	$(PYTHON) $(SCRIPTS_DIR)/build.py --html cv

html-cover-letter:
	$(PYTHON) $(SCRIPTS_DIR)/build.py --html cover-letter

html-leadership-resume:
	$(PYTHON) $(SCRIPTS_DIR)/build.py --html leadership-resume

# Run regression tests
test:
	$(PYTHON) -m unittest tests/test_document_generator.py tests/test_generator_structure.py

# Check Python syntax without running the generator
syntax:
	$(PYTHON) -m py_compile $(SCRIPTS_DIR)/generate.py $(SCRIPTS_DIR)/build.py $(SCRIPTS_DIR)/validate_yaml.py $(SCRIPTS_DIR)/document_generator/*.py tests/test_document_generator.py tests/test_generator_structure.py

# Validate all config and content YAML files
validate-yaml:
	$(PYTHON) $(SCRIPTS_DIR)/validate_yaml.py

# Full local verification path
verify: test syntax validate-yaml all html

# Clean up generated files and build artifacts
clean:
	rm -rf $(GENERATED_DIR)/*.tex $(OUTPUT_DIR)/*.pdf $(OUTPUT_DIR)/*.html $(OUTPUT_DIR)/*.json $(OUTPUT_DIR)/*.aux $(OUTPUT_DIR)/*.log $(OUTPUT_DIR)/*.out
	find $(GENERATED_DIR) -name "*.aux" -delete 2>/dev/null || true
	find $(GENERATED_DIR) -name "*.log" -delete 2>/dev/null || true
	find $(GENERATED_DIR) -name "*.out" -delete 2>/dev/null || true
