# Global agent instructions

This file is the canonical set of global instructions for every agent on this
machine. `deploy.sh` links it to:

- `~/.config/opencode/AGENTS.md` (OpenCode)
- `~/.claude/CLAUDE.md` (Claude Code)

Project-level instruction files still take precedence where they exist. Edit
this file here, not the deployed symlinks.

## Worktrees

- Create new worktrees under `.worktrees/` at the project root.
- Before creating one, verify the directory is ignored:
  `git check-ignore -q .worktrees`; if it is not, add `.worktrees/` to the
  project's `.gitignore` first.
- Prefer the harness's native worktree tool. Fall back to
  `git worktree add .worktrees/<name> -b <branch>` only when no native tool
  exists.
- Do not create worktrees outside the project directory.