# Build Official Documents

Refresh Brandon's official public PDFs and portfolio export through the
documented pipeline.

Use `.claude/skills/document-generator/SKILL.md` as the workflow source of
truth. This command is for official public outputs only.

Steps:

1. Run `make validate`.
2. Run `make all`.
3. Run `make export`.
4. Run `make privacy-scan`.
5. If layout, templates, generated TeX, or PDFs changed, render pages with
   `pdftoppm` and inspect for overlap, clipped text, and blank pages.
6. Report generated PDFs, export status, and any expected public contact
   surfaces reported by the privacy scan.
