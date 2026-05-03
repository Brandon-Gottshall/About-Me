# Archive Run

Create or update a private tailored-generation archive run.

Steps:

1. Confirm `CUSTOM_GENERATION_ARCHIVE_ROOT` points outside this public repo.
2. Run the archive helper with `ARCHIVE_AGENT_TOOL=claude` or `--tool claude`.
3. Store raw job descriptions, prompts, selected facts, generated drafts,
   validation/build results, and final decision metadata only in the private
   archive target.
4. Run `git status --short` in this public repo and confirm no raw run artifacts
   are tracked here.

Helper:

```bash
ARCHIVE_AGENT_TOOL=claude python plugins/document-generator/scripts/archive_generation.py \
  --company "Company" \
  --role "Role" \
  --source-url "https://example.com/job"
```
