# Claude Code Handoff Brief

This handoff is for a later Claude Code implementation pass. Do not paste raw
private generation archives into a public thread.

## Repository

- Public repo: `https://github.com/Brandon-Gottshall/About-Me`
- Purpose: official YAML-driven LaTeX document system for Brandon Gottshall's
  resume, CV, cover letters, portfolio exports, and agent-assisted tailored
  document generation.

## Current Foundation

- Official source data lives in `content/`.
- Document configuration lives in `config/`.
- Generator/build/validation/export code lives in `document_pipeline/` with
  compatibility wrappers in `scripts/`.
- Public official PDFs live in `output/`.
- Static portfolio export lives in `exports/profile.json`.
- Codex repo-local plugin lives in `plugins/document-generator/`.
- Private custom-generation archive contract is documented in
  `docs/ARCHIVE_CONTRACT.md`.

## Claude Code Scope

Build Claude-facing workflow support that mirrors the Codex plugin behavior:

1. Inspect official profile data without inventing facts.
2. Validate YAML and build official PDFs through repo commands.
3. Draft tailored resume/CV/cover-letter artifacts from job descriptions.
4. Archive full provenance to the private companion repo configured by
   `CUSTOM_GENERATION_ARCHIVE_ROOT`.
5. Keep raw job descriptions, prompts, and private run archives out of public git.

## Required Guardrails

- Read `AGENTS.md` and `PROVENANCE.md` before editing.
- Treat `content/` as source of truth.
- Do not claim whole-repo MIT while Awesome CV assets remain.
- Do not transmit or publish private archive content without explicit approval.
- Run `make validate`, `make test`, `make all`, `make export`, and
  `make privacy-scan` before proposing changes.

## Starter Prompt for Claude Thread

You are working on Brandon Gottshall's `About-Me` repo. Build Claude Code support
that mirrors the repo-local Codex `document-generator` plugin. Start by reading
`AGENTS.md`, `PROVENANCE.md`, `docs/ARCHIVE_CONTRACT.md`, and
`plugins/document-generator/skills/document-generator/SKILL.md`. Do not edit
official content or publish/transmit private archive material unless explicitly
approved. Focus on Claude-facing ergonomics for validation, generation,
tailored drafts, and private archive provenance.
