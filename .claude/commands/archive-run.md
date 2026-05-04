# Archive Run

Create or update a private tailored-generation archive run.

Use `.claude/skills/document-generator/SKILL.md` as the workflow source of
truth. This command adds the archive-specific preflight and output contract.

Steps:

1. Confirm `CUSTOM_GENERATION_ARCHIVE_ROOT` points outside this public repo.
   If it is unset, show Brandon this setup command before continuing:

```bash
export CUSTOM_GENERATION_ARCHIVE_ROOT="$HOME/Documents/GitHub/about-me-generations"
```

2. Prefer the private repo environment helper when available:

```bash
source "$HOME/Documents/GitHub/about-me-generations/scripts/env.sh"
```

3. Run the archive helper with `ARCHIVE_AGENT_TOOL=claude` or `--tool claude`.
4. Store raw job descriptions, prompts, selected facts, generated drafts,
   validation/build results, and final decision metadata only in the private
   archive target.
5. Validate the private archive after adding run materials:

```bash
cd "$CUSTOM_GENERATION_ARCHIVE_ROOT"
make validate
```

6. Run `git status --short` in this public repo and confirm no raw run artifacts
   are tracked here.

Helper:

```bash
ARCHIVE_AGENT_TOOL=claude python plugins/document-generator/scripts/archive_generation.py \
  --company "Company" \
  --role "Role" \
  --source-url "https://example.com/job"
```

Output:

- Private run path
- Manifest validation status
- Selected source facts, cited as `content/<file>.yaml:<key>`
- Build/validation/privacy results when available
- Public repo cleanliness status
