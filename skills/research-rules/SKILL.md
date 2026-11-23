---
name: research-rules
description: Use when researching, exploring, searching for, or fetching online information — web pages, docs, PDFs, forum/issue threads, vendor specs — to answer a question, verify a claim, or produce a report, and before writing down any web-sourced conclusion or figure.
---

# Research Rules

## Overview

**Core principle:** a conclusion is only as strong as the source you can hand over. Save sources locally **as you go**; never reconstruct them later. Every conclusion must trace to a saved file plus the URL and time you saw it.

## When to Use

- Any task that finds, verifies, or synthesizes online information.
- Resuming an interrupted research task (see rule 6).
- **Symptom you are about to violate this:** you are about to write a report or answer containing a figure/claim, with no local copy of the page that proves it.

Not for: pure local codebase exploration, or throwaway lookups you will never cite.

## Outputs — shared, conventional names

Write these at the **workspace root** with ordinary names so other agents and skills can read them directly. Never hide research artifacts in a private, tool-specific directory.

| Path | Purpose |
|------|---------|
| `PLAN.md` | agenda: questions to answer, approach, scope |
| `PROGRESS.md` | running log; makes the task resumable |
| `sources/<slug>/original.<ext>` | raw page exactly as served (`.html`/`.pdf`/`.json`) |
| `sources/<slug>/<slug>.md` | clean markdown derivative |
| `sources/INDEX.md` | source ↔ URL ↔ conclusion |

## Rules

1. **Plan first.** Before the first fetch, create `PLAN.md` (questions, approach, scope). Update it whenever scope changes.
2. **Capture every supporting source.** Save every page that *directly* supports a conclusion, plus relevant upstream pages (the hop that led you there) when they carry evidence. Skip pure search-result/aggregator pages. If a page is paywalled or unusable, log it in the index — **never silently drop it**.
3. **Raw + clean, both.** For each source store the raw artifact as served (`original.html`) **and** a clean derivative (`<slug>.md`). Best effort — but the *real* best effort, not "I cited the URL". If a clean conversion genuinely fails, say so in the index.
4. **Two timestamps, ISO-8601 with time and timezone where possible.** (a) **visit time** = now; (b) the **resource's own time** = its publication or last-updated date, which may be years older. Never conflate them.
5. **Maintain `PROGRESS.md` and `sources/INDEX.md` continuously.** `PROGRESS.md`: done / next / open questions / blockers, each entry timestamped. `sources/INDEX.md`: each source's URL, both times, and the conclusion it supports.
6. **Resuming.** On resume, read `PLAN.md` and `PROGRESS.md` **first**, then continue from the recorded "next" step.
7. **Isolate tooling.** **REQUIRED SUB-SKILL:** use **env-isolation** for anything you install. Install into a workspace-local environment; never install globally. (If `env-isolation` is unavailable, follow that principle directly.)

## Converting pages

- **Discover an appropriate tool**, then prefer an installed skill or MCP over ad-hoc commands. Check your available skills, MCP servers, and CLIs for one that fits the source format. The following are *examples, not the only options*:
  - `baoyu-url-to-markdown` — interactive / JS-rendered HTML (requires `bun`).
  - the `pdf` skill — PDFs (`pdftotext`, `pdfplumber`).
- Raw bytes: `curl` or `webfetch`.
- If a required tool is missing, install it workspace-locally — see the **env-isolation** skill.

## Red Flags — stop and comply

- "The URL in my report is enough." → URLs rot and change; the saved bytes are the evidence. If you cite it, save it.
- "I'll save everything at the end." → interruptions are exactly why you save as you go.
- "Saving is overkill for a quick lookup." → if you will cite it, save it.
- "It was only a search-result page." → fine, but the page you clicked *through* is a source.
- A finished report with no `sources/`, no `PROGRESS.md`, or no times on the sources.