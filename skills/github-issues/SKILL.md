---
name: github-issues
description: Read and understand a long GitHub issue or pull request from a normalized local file. Use when the user shares an issue/PR URL, asks about a discussion thread, or needs to know where a long-running issue stands.
---

# GitHub issues

Reading a 200-comment thread by pouring tool output into context wastes the window and
produces a summary of the *first* comments rather than of the thread. Fetch it to a file
and navigate the file.

## Fetch

`scripts/issue-md` sits beside this file. Run it via the skill's base directory:

```sh
<base>/scripts/issue-md OWNER/REPO NUMBER [-o DIR] [--deep]
```

Output defaults to `./.gh-issues/OWNER-REPO-N.md`. Before the first fetch in a
repository, make sure `.gh-issues/` is gitignored so fetched threads can never be
committed — private threads and usernames end up in these files.

Cost, at 100 comments per request:

| part | requests |
|---|---|
| issue body + first comment page | 2 |
| each additional 100 comments | +1 |
| history (labels, assignment, close/reopen) | +1 |
| reviews + inline comments (PR only) | +2 |
| `--deep` (timeline, for cross-references) | +1…+several |

A 392-comment thread is about 6 requests. Unauthenticated that is 60/hour total, so
prefer `GITHUB_TOKEN` for anything beyond a one-off — it also unlocks private repos.
Re-runs are conditional (ETag), so unchanged pages cost no bandwidth; unauthenticated
304s still consume quota.

## Read

1. Start with the header block: stream counts, date span, most active participants.
2. `grep -n '^## [CRIHX][0-9]' FILE` for the section index.
3. Read the body, then skim headers only. Read ranges around the `C` numbers that matter.
4. `## H<n>` is state history: labels, assignment, close/reopen, referenced commits, and
   `comment_deleted`. Deleted content is **not recoverable**, so if you see one, say the
   thread may have gaps instead of implying completeness.
5. `## X<n>` (only with `--deep`) is the cross-references — usually where "superseded by
   #1234" or "duplicate of …" lives.

## Delegate when long

Above roughly 150 comments, dispatch a subagent rather than reading inline: give it the
file path and ask for the opening claim, what changed over time, where it stands, and
the unresolved disputes — citing `C`/`R`/`I` numbers. The transcript then stays out of
the primary context.

## Report

- what the opening post claims, with repro steps if any
- what changed as the thread developed (status flips, maintainer answers, workarounds)
- where it stands now: resolved, stalled, or disputed about *what*
- PRs: review verdicts (`R`) and unresolved inline concerns (`I`)
- who is worth reading (highest counts, plus anyone who sounds like a maintainer)

Cite `C`/`R`/`I`/`H`/`X` numbers so the user can jump to the part you mean. Quote short
excerpts only; never paste whole comments back.

## Limitations

- Deleted comments are gone from the API; edited comments show only current text.
- Minimized comments ("off-topic", "outdated") are included but not flagged as such.
- GitHub Discussions are not issues, and this does not cover them.
- Web-page collapse ("Load more", hidden middle) does **not** affect the output — the
  REST API returns the complete collection regardless of what the page renders.