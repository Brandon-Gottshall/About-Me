# Promote Example

Plan promotion of a private tailored-generation run into a sanitized public
example.

Use `.claude/skills/document-generator/SKILL.md` as the workflow source of
truth. This command is checklist-only by default: do not copy files from the
private archive into this public repo unless Brandon explicitly approves the
specific sanitized files to publish.

Steps:

1. Read `docs/ARCHIVE_CONTRACT.md`.
2. Confirm the candidate run can be represented as `sanitized-public-example`.
3. Identify every raw input, prompt, note, selected fact, draft, and artifact that
   would be touched.
4. Produce a redaction plan:
   - remove or summarize third-party job description text
   - remove recruiter or company contact details unless already public
   - keep Brandon's contact details limited to public fields already in `output/`
   - remove private strategy notes or sensitive reasoning
5. Produce a diff plan listing proposed public paths, expected content shape, and
   validation commands.
6. After Brandon approves implementation, apply only sanitized files and run:

```bash
make validate
make test
make privacy-scan
```

Output:

- Candidate run id or path
- Publication eligibility
- Redaction plan
- Proposed public file paths
- Validation/privacy commands to run
- Explicit approval needed before implementation
