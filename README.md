# myai

Portable home for my own coding/agent customizations — starting with skills.

The point of this repo is **ownership**, not aggregation. Anything here is
maintained by me. Anything that can be found, installed, and updated upstream
is *not* copied in; it is recorded in [`THIRD-PARTY.md`](THIRD-PARTY.md) with
its provenance. This keeps the repo small, auditable, and free of upstream
drift and license surprises.

The repo is public. Do not commit secrets, tokens, fetched private threads,
or machine-specific absolute paths.

## Layout

```
myai/
├── README.md          # this file
├── THIRD-PARTY.md     # index of upstream skills, never their content
├── deploy.sh          # link skills/ into installed agents, apply config
├── .gitignore
├── config/
│   ├── apply.py       # merge repo config fragments into global tool config
│   └── opencode/
│       └── worktree.jsonc
├── instructions/
│   └── AGENTS.md      # reference snippet; not deployed
└── skills/            # first-party skills only, one directory each
    ├── env-isolation/
    ├── github-issues/
    └── research-rules/
```

Each skill is self-contained: `SKILL.md` plus its own `scripts/`,
`references/`, or `assets/`. No skill depends on files in a sibling skill, so
any one can be linked or copied independently.

## Ownership rule

> Put something in `skills/` only if I am the author/maintainer.
> If upstream maintains it, add a row to `THIRD-PARTY.md` instead.

Adapted-from-upstream work belongs in `THIRD-PARTY.md` too, unless the
divergence is large enough that upstream updates no longer apply — then it
becomes first-party, with the origin recorded in its `SKILL.md`.

## Deploy

`deploy.sh` symlinks each first-party skill into the skill directory of every
**installed** agent, then merges the OpenCode config fragment:

| Tool | Skills target | Config target |
|------|---------------|---------------|
| OpenCode | `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/` | `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/opencode.json(c)` |
| Claude Code | `$HOME/.claude/skills/` | — |

Skill directories and config files are created only when the tool's config
directory already exists.

Global instruction files (`AGENTS.md`, `CLAUDE.md`, ...) are deliberately never
written: they belong to the agent's owner and may hold unrelated instructions.
Use the agent's own mechanism, or a project-level instruction file, for that.

```sh
./deploy.sh --dry-run   # show actions, change nothing
./deploy.sh             # apply
./deploy.sh --tool opencode
./deploy.sh --force     # back up conflicts and allow config replacement
./deploy.sh --create    # also create config dirs for tools not installed
```

Behaviour:

- Missing tools are skipped, not created (unless `--create`).
- Existing links already pointing here are left alone; re-running is safe.
- A real directory or foreign link in the way is reported and skipped. With
  `--force` it is renamed to `<name>.bak.<timestamp>` first, never deleted.
- Third-party skill directories are never touched.
- Skill links and the config merge use the same link and conflict rules;
  unresolved conflicts exit non-zero.

### First-time adoption

If a tool directory already contains a real copy of a skill that now lives
here, deploys will report a conflict. Move that copy aside yourself, then
re-run `./deploy.sh` — or use `--force` to let the script back it up.

## Portable tool settings

`config/` holds secret-free fragments of tool configuration. The real global
config is never committed: it contains provider credentials. Instead,
`config/apply.py` merges one fragment key into it, preserving everything else
and backing the file up first. `deploy.sh` runs it automatically for OpenCode;
invoke it directly only for a one-off run or a custom config path.

The current fragment, `config/opencode/worktree.jsonc`, sets OpenCode's
`worktree.directory` to `.worktrees`. `apply.py` uses only the Python 3
standard library.

```sh
./config/apply.py --dry-run   # show the change
./config/apply.py             # apply
./config/apply.py --force     # replace a different value, or rewrite a
                              # commented JSONC file (comments are lost)
./config/apply.py --config /path/to/opencode.jsonc
```

Behaviour:

- Only the `worktree` key is added or replaced; providers, models, plugins,
  MCP servers, and credentials are left alone.
- If the file is missing, a minimal config with `$schema` is created (when the
  OpenCode config directory exists, or with `--create`).
- A JSONC file containing comments is not rewritten without `--force`, because
  comments cannot survive a rewrite.
- The value is valid globally and per project. Relative paths resolve against
  each project's canonical checkout, so every project gets its own
  `.worktrees/`.

The same convention applies when agents create worktrees manually (or in tools
without a native worktree setting, such as Claude Code):
[`instructions/AGENTS.md`](instructions/AGENTS.md) is the canonical text for it.
That file is not deployed by `deploy.sh`; copy what you need into a project's
own `AGENTS.md`/`CLAUDE.md`, or into your own global instruction file. This
repository's own `.gitignore` ignores `.worktrees/`.

## Add a first-party skill

```sh
cp -a path/to/skill skills/<name>
./deploy.sh --dry-run
./deploy.sh
```

Requirements:

- Directory name matches the frontmatter `name` (lowercase, hyphenated).
- `SKILL.md` has `name` and `description` frontmatter.
- Scripts are self-contained and use workspace-local environments
  (see `skills/env-isolation`).
- No secrets, credentials, or captured private data.

## Add a third-party skill

Do not copy it in. Add a row to `THIRD-PARTY.md` with the upstream repo,
subpath, ref, version, license, and how/where it is installed. Install it with
its own mechanism (cc-switch, the upstream repo, a plugin marketplace, etc.).

## Verify

Deployment only changes agent config directories. After running it:

```sh
ls -l ~/.config/opencode/skills ~/.claude/skills
readlink -f ~/.config/opencode/skills/<name>
grep -A2 '"worktree"' ~/.config/opencode/opencode.jsonc
```

Then start the agent and confirm the skill appears and new worktrees land in
`.worktrees/`.

## License

No license has been chosen for this repository yet.