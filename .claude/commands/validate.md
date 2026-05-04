# Validate

Run the local validation path for the official document pipeline.

Use `.claude/skills/document-generator/SKILL.md` as the workflow source of
truth. This command is the lightweight pre-build check.

Steps:

1. Run `make validate`.
2. Run `make test`.
3. If either fails, report the failing file, command, and smallest safe fix.
4. Do not edit personal content unless Brandon explicitly asks for that change.
