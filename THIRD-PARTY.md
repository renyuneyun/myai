# Third-party skills

Upstream skills I use but do **not** maintain and do **not** copy into this
repo. They are installed by their own mechanism (currently cc-switch, plus
one plugin) and updated from upstream there.

This file is an index, not an installer. Recording metadata here creates no
redistribution obligation; the content stays upstream.

## Installed via cc-switch

`Ref` is the branch cc-switch tracks. `Version` is only what the installed
copy declares; `—` means the checkout does not state one. `Snapshot` is the
first 7 characters of cc-switch's content hash for the installed copy, so a
future upstream change can be told apart from the copy that was reviewed.

| Skill | Upstream | Subpath | Ref | Version | License | Snapshot | Installed |
|-------|----------|---------|-----|---------|---------|----------|-----------|
| `pdf` | `anthropics/skills` | `skills/pdf` | main | — | Proprietary (Anthropic) | `6a01b6d` | 2026-05-04 |
| `baoyu-url-to-markdown` | `JimLiu/baoyu-skills` | `skills/baoyu-url-to-markdown` | main | 1.61.0 | Not stated in checkout | `c615e19` | 2026-05-04 |
| `guizang-ppt-skill` | `op7418/guizang-ppt-skill` | `/` (repo root) | main | — | AGPL-3.0 | `304119e` | 2026-09-19 |
| `visual-explainer` | `nicobailon/visual-explainer` | `plugins/visual-explainer` | main | 0.11.0 | MIT | `029446d` | 2026-09-19 |
| `dashi-ppt` | `chuspeeism/dashi-ppt-skill` | `skills/dashi-ppt` | main | 0.4.14 | Not stated in checkout | `caaccfc` | 2026-09-19 |
| `html-to-image-automation` | `ComposioHQ/awesome-claude-skills` | `composio-skills/html-to-image-automation` | master | — | Not stated in checkout | `147189b` | 2026-09-19 |
| `frontend-slides` | `zarazhangrui/frontend-slides` | `plugins/frontend-slides/skills/frontend-slides` | main | — | Not stated in checkout | `9dfe641` | 2026-09-19 |
| `frontend-design` | `anthropics/skills` | `skills/frontend-design` | main | — | Apache-2.0 | `7e9c2af` | 2026-09-19 |

All rows use `https://github.com/<upstream>`. cc-switch syncs them as copies
(`skillSyncMethod: copy`), so `~/.config/opencode/skills/` and
`~/.cc-switch/skills/` may each hold a copy. That duplication is expected;
pruning it is a separate cleanup and deliberately not part of this repo.

## Installed as a plugin

| Skill set | Upstream | Notes |
|-----------|----------|-------|
| `understand`, `understand-chat`, `understand-dashboard`, `understand-diff`, `understand-domain`, `understand-explain`, `understand-figma`, `understand-knowledge`, `understand-onboard` | `Egonex-AI/Understand-Anything` | Local plugin at `~/.understand-anything/repo`; exposed through `~/.agents/skills/` symlinks. cc-switch also keeps local copies. |

## Not indexed here

- `superpowers` — an OpenCode/Claude Code **plugin**
  (`git+https://github.com/obra/superpowers.git`), not a skill directory.
- Skills bundled with an agent installation itself.
- Skills that enter a project locally via `.opencode/skills/` or
  `.claude/skills/` in that project.

## Maintenance

When adding an upstream skill: install it with its own tool, then add a row
with upstream repo, subpath, ref, version, license, and snapshot/date. When
removing one: remove the row after uninstalling it upstream-side. When a
license is unclear, leave `Not stated in checkout` rather than guessing.