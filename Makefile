.PHONY: all clean

# Compiler
CC = xelatex

# Directories
SRC_DIR = src/resume
OUTPUT_DIR = output

# Source files
RESUME_TEX = $(SRC_DIR)/resume.tex
RESUME_PDF = $(OUTPUT_DIR)/resume.pdf

# Ensure output directory exists
$(shell mkdir -p $(OUTPUT_DIR))

# Default target
all: resume

# Build resume
resume: $(RESUME_PDF)

$(RESUME_PDF): $(RESUME_TEX)
	cd $(SRC_DIR) && $(CC) -output-directory=../../$(OUTPUT_DIR) -interaction=nonstopmode -halt-on-error $(notdir $<)

# Clean up
clean:
	rm -rf $(OUTPUT_DIR)/*.pdf $(OUTPUT_DIR)/*.aux $(OUTPUT_DIR)/*.log $(OUTPUT_DIR)/*.out
