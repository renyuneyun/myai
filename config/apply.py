#!/usr/bin/env python3
"""Apply myai's OpenCode config fragment to the user's global config.

Currently applies `config/opencode/worktree.jsonc` (the `worktree` key) to
`${XDG_CONFIG_HOME:-~/.config}/opencode/opencode.json(c)`.

Safety rules:
  * Only the described key is added or replaced; every other setting, including
    provider credentials, is preserved.
  * The existing file is backed up with `copy` before writing.
  * A JSONC file containing comments is not rewritten unless --force is given,
    because a rewrite cannot preserve the comments.
  * --dry-run changes nothing.

Exit status: 0 on success/no-op, 1 on a refused conflict, 2 on bad input.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
FRAGMENT = REPO_DIR / "config" / "opencode" / "worktree.jsonc"
SCHEMA = "https://opencode.ai/config.json"


def strip_comments(text):
    """Remove // and /* */ comments, respecting string literals."""
    out = []
    i = 0
    n = len(text)
    in_string = False
    escaped = False
    had_comments = False

    while i < n:
        char = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue

        if char == '"':
            in_string = True
            out.append(char)
            i += 1
            continue

        if char == "/" and nxt == "/":
            had_comments = True
            i += 2
            while i < n and text[i] not in "\r\n":
                i += 1
            continue

        if char == "/" and nxt == "*":
            had_comments = True
            i += 2
            while i < n - 1 and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue

        out.append(char)
        i += 1

    return "".join(out), had_comments


def strip_trailing_commas(text):
    """Remove commas that are followed only by whitespace and } or ]."""
    out = []
    i = 0
    n = len(text)
    in_string = False
    escaped = False

    while i < n:
        char = text[i]

        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue

        if char == '"':
            in_string = True
            out.append(char)
            i += 1
            continue

        if char == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j < n and text[j] in "}]":
                i += 1
                continue

        out.append(char)
        i += 1

    return "".join(out)


def parse_jsonc(text):
    stripped, had_comments = strip_comments(text)
    stripped = strip_trailing_commas(stripped)
    return json.loads(stripped), had_comments


def insert_top_level(text, key, value):
    """Insert a top-level key into a comment-free JSON object, preserving text."""
    index = text.rfind("}")
    if index < 0:
        raise ValueError("no closing brace found")

    head = text[:index]
    tail = text[index:]

    j = len(head) - 1
    while j >= 0 and head[j] in " \t\r\n":
        j -= 1
    if j < 0:
        raise ValueError("empty configuration document")

    separator = "\n" if head[j] in "{," else ",\n"
    literal = json.dumps(value, ensure_ascii=False, indent=2)
    literal = literal.replace("\n", "\n  ")
    block = '%s  "%s": %s\n' % (separator, key, literal)
    return head + block + tail


def config_path(explicit):
    if explicit:
        return Path(explicit).expanduser()

    root = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")) / "opencode"
    for name in ("opencode.jsonc", "opencode.json"):
        candidate = root / name
        if candidate.exists():
            return candidate
    return root / "opencode.jsonc"


def main():
    parser = argparse.ArgumentParser(
        description="Apply myai's OpenCode worktree config to the global config."
    )
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="show the change without writing anything")
    parser.add_argument("-f", "--force", action="store_true",
                        help="replace an existing worktree value and rewrite a "
                             "commented JSONC file (comments are lost)")
    parser.add_argument("-c", "--create", action="store_true",
                        help="create the OpenCode config directory if it is missing")
    parser.add_argument("--config", metavar="PATH",
                        help="explicit config file to update")
    args = parser.parse_args()

    if not FRAGMENT.is_file():
        print("error: fragment not found: %s" % FRAGMENT, file=sys.stderr)
        return 2

    try:
        fragment, _ = parse_jsonc(FRAGMENT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("error: cannot read %s: %s" % (FRAGMENT, exc), file=sys.stderr)
        return 2

    desired = fragment.get("worktree")
    if not isinstance(desired, dict) or desired.get("directory") != ".worktrees":
        print("error: %s must define worktree.directory = \".worktrees\"" % FRAGMENT,
              file=sys.stderr)
        return 2

    target = config_path(args.config)

    if target.is_symlink():
        resolved = target.resolve()
        print("note: %s is a symlink; updating %s" % (target, resolved))
        target = resolved

    if not target.parent.exists():
        if not args.create:
            print("skip: %s does not exist (use --create)" % target.parent)
            return 0
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)

    exists = target.exists()
    if exists:
        try:
            text = target.read_text(encoding="utf-8")
            data, had_comments = parse_jsonc(text)
        except (OSError, json.JSONDecodeError) as exc:
            print("error: cannot parse %s: %s" % (target, exc), file=sys.stderr)
            return 2
        if not isinstance(data, dict):
            print("error: %s does not contain a JSON object" % target, file=sys.stderr)
            return 2
    else:
        text = json.dumps({"$schema": SCHEMA}, indent=2) + "\n"
        data = {"$schema": SCHEMA}
        had_comments = False

    current = data.get("worktree")
    if current == desired:
        print("%s: worktree is already set to %s" %
              (target, json.dumps(desired, ensure_ascii=False)))
        return 0

    if current is not None and not args.force:
        print("%s: worktree is already configured differently:" % target)
        print("  " + json.dumps(current, ensure_ascii=False))
        print("Refusing to change it; re-run with --force to replace it.")
        return 1

    if current is None and not had_comments:
        try:
            new_text = insert_top_level(text, "worktree", desired)
        except ValueError as exc:
            print("error: cannot insert into %s: %s" % (target, exc), file=sys.stderr)
            return 2
    else:
        if had_comments and not args.force:
            print("%s: file contains comments; refusing to rewrite it." % target)
            print("Add this key manually, or re-run with --force (comments will be lost):")
            print(json.dumps({"worktree": desired}, ensure_ascii=False, indent=2))
            return 1
        data["worktree"] = desired
        new_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    try:
        verified, _ = parse_jsonc(new_text)
    except json.JSONDecodeError as exc:
        print("error: generated config does not parse (%s); nothing written" % exc,
              file=sys.stderr)
        return 2
    if verified.get("worktree") != desired:
        print("error: generated config does not contain the expected value; "
              "nothing written", file=sys.stderr)
        return 2

    if args.dry_run:
        print("would update %s: worktree = %s" %
              (target, json.dumps(desired, ensure_ascii=False)))
        return 0

    if exists:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_name(target.name + ".bak." + stamp)
        shutil.copy2(target, backup)
        print("backup: %s" % backup)

    temporary = target.with_name(target.name + ".tmp." + str(os.getpid()))
    temporary.write_text(new_text, encoding="utf-8")
    os.replace(temporary, target)
    print("updated %s: worktree = %s" %
          (target, json.dumps(desired, ensure_ascii=False)))
    return 0


if __name__ == "__main__":
    sys.exit(main())