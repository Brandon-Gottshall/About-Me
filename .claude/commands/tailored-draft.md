# Tailored Draft

Create a job-specific resume, CV, or cover-letter draft without contaminating
the public source of truth.

Use `.claude/skills/document-generator/SKILL.md` as the workflow source of
truth. This command defines the tailored-draft output contract.

Rules:

- Use only source facts from `content/`.
- Cite selected facts as `content/<file>.yaml:<key>` or a more precise dotted
  key when needed.
- Do not invent experience, credentials, employment dates, metrics, or contact
  data.
- Do not commit raw job descriptions, prompts, recruiter contact data, or draft
  artifacts to this public repo.
- Use `prompts/document-generator/tailored-system.md` and
  `prompts/document-generator/tailored-task.md` as the drafting frame.
- Archive provenance privately before considering a draft complete.

Output:

- Job-fit interpretation
- Selected source facts with citations
- Draft content
- Suggested official source changes, if any
- Archive status
- Validation/build/privacy status
- Explicit assertion that no facts were invented
