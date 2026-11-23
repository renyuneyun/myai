---
name: env-isolation
description: Use when a task needs to install or run external tools, interpreters, package managers, CLIs, or libraries — so they stay isolated per workspace and never pollute the system, home directories, or shared caches.
---

# Environment Isolation

## Overview

**Core principle:** never install globally. Every tool, library, and cache a workspace needs lives **inside that workspace**, so projects don't collide and the host stays clean. Create an environment on demand; don't lean on the system's.

## When to Use

- Installing or running any external tool: Python/Ruby/Node/Bun/Rust/Go CLIs, libraries, package managers, compilers.
- **Symptom you are about to violate this:** you are about to run `pip install`, `npm install -g`, `apt`, or `sudo` against the system — or a tool is about to land in `~/.cache`, `~/.local`, or `/usr/local`.

Not for: tools already on `PATH` that need no install.

## Layout

Keep environments under **`.envs/`** at the workspace root, one subdirectory per runtime. Ecosystems whose loader requires a fixed path keep their conventional workspace-local location (e.g. `node_modules/`, `vendor/`); point their *caches* under `.envs/` too. Add `.envs/` to the workspace `.gitignore`.

| Runtime | Location | Setup |
|---------|----------|-------|
| Python | `.envs/venv` | `uv venv .envs/venv` · `uv pip install --python .envs/venv/bin/python PKG` · run `.envs/venv/bin/PKG` |
| Node / npm | `.envs/node` (prefix + cache) + project `node_modules/` | `npm --prefix .envs/node …` · `npm_config_cache=.envs/node/cache npm install …` |
| Bun | `.envs/bun` | `BUN_INSTALL="$PWD/.envs/bun"` |
| Rust | `.envs/cargo` | `CARGO_HOME="$PWD/.envs/cargo"` |
| Go | `.envs/go` | `GOPATH="$PWD/.envs/go"` |
| Ruby | `.envs/bundle` | `BUNDLE_PATH=.envs/bundle` |
| Conda | `.envs/conda` | `conda create -p .envs/conda` |

## Rules

1. **On demand.** Create an environment lazily, only when a tool is actually needed — never preemptively.
2. **Workspace-local.** Nothing in the system, `~/.cache`, `~/.local`, or `/usr/local`. Point package-manager caches (pip, npm, uv) at `.envs/` too.
3. **Explicit invocation.** Call tools by path (`.envs/venv/bin/tool`); don't rely on shell activation that won't persist between commands.
4. **Prefer curated defaults.** Python → `uv`. Install the minimum needed.
5. **Self-contained and reproducible.** Keep `.envs/` out of git; record the setup command where the project will find it (README or notes) so the environment can be rebuilt.
6. **Never `sudo`** for project tooling.

## Red Flags — stop and comply

- `pip install X` against a system (often externally-managed) Python → use `.envs/venv`.
- `npm install -g`, or a bare `npx` that writes the shared `~/.npm` cache → install into `.envs/node` and set `npm_config_cache`.
- A tool or cache appearing in `~/.local/bin`, `~/.cache/uv`, or `~/.cache/pip`.
- `uvx` looks convenient, but it shares uv's global cache — when a tool will be reused, install it into `.envs/venv` instead.
- Two different workspaces sharing one environment — environments are per-workspace.