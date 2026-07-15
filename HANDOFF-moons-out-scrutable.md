# HANDOFF — for the session adding Moons Out departure + Scrutable

**From:** Claude Code session `febff905-3b89-4747-a1d3-33409313a2f6` (resume/portfolio UX session, 2026-07-14)
**To:** session `019f4f9d-cfab-71e3-b0d0-504d014638c3` (or whichever session lands the Moons Out/Scrutable record updates)
**Delete this file once incorporated.**

This repo took 7 commits today (through `c310faa`) plus the portfolio repo's
`ux/critique-fixes` branch (9 commits). Relayer your narrative changes **on top
of** this state — do not write against an older reading of the record.

## Already done here — do not redo

- `content/core/experience.yaml`: title is **Engineer Electrical Systems
  Technician**; new bullets — AMMPS micro-grids; Incirlik 2017 deployment
  (VMAQ-3 electronic warfare vs Da'esh under OIR); two-Marine power team
  keeping gen site, HVAC, and power distribution online, carrying comms through
  active grid outages; Assistant Maintenance Chief opens with the E-5
  billet-filled-as-E-4 line; QC NCO opens with the billet turnover to the
  incoming sergeant. Phrase of record: "life-sustaining critical utilities
  infrastructure". Locations: "Remote — Ohio" (Moons Out), "Remote — New York"
  (Nebula).
- `content/optional/certifications.yaml`: EPA 608 enriched (No expiration +
  qualifier line tying it to utilities work).
- `content/core/summary.yaml`: new `cv:` key; per-doc-type summaries are
  supported in `document_pipeline/sections.py` + `html_sections.py`.
- `content/core/personal.yaml`: `position.cv` = "Software Engineer •
  Marine~Corps Veteran" (Technical Director retired after the departure);
  `quote.cv` emptied — `templates/base_cv.tex` now guards empty quotes.
- `content/optional/projects.yaml`: populated (5 entries); `config/documents.yaml`
  cv sections include `projects`; project `\cventry` field order fixed in
  `document_pipeline/latex.py` so names render bold.

## Yours to do

1. **Moons Out end date + past tense** in BOTH `content/core/experience.yaml`
   and `content/optional/leadership.yaml` — both still read "Mar 2025 - Present".
2. **Scrutable / Scrutable Commons entries** wherever they belong in the record.
3. `content/core/summary.yaml` `text:` (the resume summary) is a stale
   front-end-pitch paragraph — rewrite consistent with the new arc.
4. Keep the narrative order: technician → Incirlik deployment → ahead-of-grade
   billet → QC → software/teaching → **Scrutable as current focus**.
5. The portfolio About page (branch `ux/critique-fixes`,
   `src/app/about/page.tsx`) already says "a run as technical director at an
   Ohio media studio. Now I'm studying data science and building Scrutable, a
   community-education effort." Upgrade that descriptor to match your settled
   Scrutable framing so site and documents agree.

Run after editing: `make validate && make test && make all && make export &&
make privacy-scan`. Both repos are local-only; Brandon gates pushes.
