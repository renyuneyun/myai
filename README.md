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
├── deploy.sh          # link skills/ into installed agents
├── .gitignore
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
**installed** agent:

| Tool | Target | Created when |
|------|--------|--------------|
| OpenCode | `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/` | the OpenCode config dir exists |
| Claude Code | `$HOME/.claude/skills/` | `~/.claude` exists |

```sh
./deploy.sh --dry-run   # show actions, change nothing
./deploy.sh             # apply
./deploy.sh --tool opencode
./deploy.sh --force     # back up conflicting entries, then link
./deploy.sh --create    # also create config dirs for tools not installed
```

Behaviour:

- Missing tools are skipped, not created (unless `--create`).
- Existing links already pointing here are left alone; re-running is safe.
- A real directory or foreign link in the way is reported and skipped. With
  `--force` it is renamed to `<name>.bak.<timestamp>` first, never deleted.
- Third-party skill directories are never touched.

### First-time adoption

If a tool directory already contains a real copy of a skill that now lives
here, deploys will report a conflict. Move that copy aside yourself, then
re-run `./deploy.sh` (or use `--force` to let the script back it up).

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
```

Then start the agent and confirm the skill appears.

## License

No license has been chosen for this repository yet.