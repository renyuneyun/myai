# Global agent instructions (reference)

This file is a canonical, copy-pasteable set of global instructions. It is
**not** deployed by `deploy.sh` and is never linked into an agent's config
directory: global instruction files belong to their owner, who may keep other
rules in them. Copy the sections you want into a project's `AGENTS.md` /
`CLAUDE.md`, or into your own global instruction file, and edit them there.

## Worktrees

- Create new worktrees under `.worktrees/` at the project root.
- Before creating one, verify the directory is ignored:
  `git check-ignore -q .worktrees`; if it is not, add `.worktrees/` to the
  project's `.gitignore` first.
- Prefer the harness's native worktree tool. Fall back to
  `git worktree add .worktrees/<name> -b <branch>` only when no native tool
  exists.
- Do not create worktrees outside the project directory.