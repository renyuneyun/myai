#!/usr/bin/env sh
# myai deploy: link first-party skills into the config dirs of installed agents.
#
# Design rules:
#   * Only directories under skills/ are deployed. Third-party skills stay
#     wherever their own installer put them and are never touched.
#   * A tool is skipped unless its config directory already exists.
#   * Existing real files, real directories, and foreign symlinks are never
#     overwritten unless --force is given; then they are backed up first.
#   * Safe to re-run: links that already point here are left alone.

set -eu

app=myai

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
skills_dir="$repo_dir/skills"

dry_run=0
force=0
create=0
want_tools=""

usage() {
	cat <<EOF
Usage: $(basename -- "$0") [options]

Link each skill under skills/ into the skill directory of every installed
agent. Tools whose config directory is missing are skipped by default.

Options:
  -n, --dry-run      Show what would change; change nothing.
  -f, --force        Back up a conflicting entry to <name>.bak.<timestamp>,
                     then create the link.
  -c, --create       Create a tool's config directory if the tool is missing.
  -t, --tool NAME    Deploy only to this tool (opencode, claude).
                     Repeatable, or comma-separated.
  -h, --help         Show this help.

Exit status: 0 on success; 1 if a conflict was left unresolved; 2 on bad usage.
EOF
}

die() {
	printf '%s: %s\n' "$app" "$1" >&2
	exit 2
}

tool_root() {
	case "$1" in
		opencode) printf '%s\n' "${XDG_CONFIG_HOME:-$HOME/.config}/opencode" ;;
		claude)   printf '%s\n' "$HOME/.claude" ;;
		*)        return 1 ;;
	esac
}

tool_selected() {
	[ -z "$want_tools" ] && return 0
	case ",$want_tools," in
		*",$1,"*) return 0 ;;
	esac
	return 1
}

add_tool() {
	case "$1" in
		opencode|claude) ;;
		*) die "unknown tool '$1' (expected opencode or claude)" ;;
	esac
	want_tools="${want_tools:+$want_tools,}$1"
}

while [ $# -gt 0 ]; do
	case "$1" in
		-n|--dry-run) dry_run=1 ;;
		-f|--force)   force=1 ;;
		-c|--create)  create=1 ;;
		-t|--tool)
			[ $# -ge 2 ] || die "--tool needs a value"
			add_tool "$2"
			shift
			;;
		--tool=*)
			add_tool "${1#--tool=}"
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			usage >&2
			die "unknown option '$1'"
			;;
	esac
	shift
done

[ -d "$skills_dir" ] || die "no skills directory at $skills_dir"

conflicts=0
linked=0
skipped=0

handle_conflict() {
	dest=$1
	src=$2
	printf 'conflict: %s exists and does not point at %s\n' "$dest" "$src" >&2

	if [ "$force" -eq 0 ]; then
		conflicts=$((conflicts + 1))
		return 0
	fi

	stamp=$(date +%Y%m%d-%H%M%S)
	backup="$dest.bak.$stamp"

	if [ "$dry_run" -eq 1 ]; then
		printf '  would move %s -> %s and link to %s\n' "$dest" "$backup" "$src"
	else
		mv -- "$dest" "$backup"
		ln -s -- "$src" "$dest"
		printf '  backed up to %s and linked\n' "$backup"
	fi
	linked=$((linked + 1))
}

deploy_tool() {
	tool=$1
	root=$(tool_root "$tool") || return 0
	dest_dir="$root/skills"

	if [ ! -d "$root" ]; then
		if [ "$create" -eq 1 ]; then
			[ "$dry_run" -eq 1 ] || mkdir -p -- "$dest_dir"
			printf 'create %s\n' "$root"
		else
			printf 'skip %s: %s not found\n' "$tool" "$root"
			return 0
		fi
	fi

	if [ ! -d "$dest_dir" ]; then
		[ "$dry_run" -eq 1 ] || mkdir -p -- "$dest_dir"
	fi

	printf '== %s -> %s\n' "$tool" "$dest_dir"

	for src in "$skills_dir"/*; do
		[ -d "$src" ] || continue

		name=$(basename -- "$src")

		if [ ! -f "$src/SKILL.md" ]; then
			printf 'skip %s: no SKILL.md\n' "$name"
			skipped=$((skipped + 1))
			continue
		fi

		dest="$dest_dir/$name"

		if [ -L "$dest" ]; then
			target=$(readlink -- "$dest" || true)
			if [ "$target" = "$src" ]; then
				printf 'ok   %s (already linked)\n' "$name"
				skipped=$((skipped + 1))
				continue
			fi
			case "$target" in
				"$skills_dir"/*)
					# A link into this repo that has gone stale (renamed or
					# removed skill). Ours to repair.
					if [ "$dry_run" -eq 1 ]; then
						printf '  would relink %s -> %s\n' "$dest" "$src"
					else
						ln -sfn -- "$src" "$dest"
						printf 'link %s (relinked)\n' "$name"
					fi
					linked=$((linked + 1))
					continue
					;;
			esac
			handle_conflict "$dest" "$src"
			continue
		fi

		if [ -e "$dest" ]; then
			handle_conflict "$dest" "$src"
			continue
		fi

		if [ "$dry_run" -eq 1 ]; then
			printf '  would link %s -> %s\n' "$dest" "$src"
		else
			ln -s -- "$src" "$dest"
			printf 'link %s\n' "$name"
		fi
		linked=$((linked + 1))
	done
}

for tool in opencode claude; do
	if tool_selected "$tool"; then
		deploy_tool "$tool"
	fi
done

if [ "$dry_run" -eq 1 ]; then
	printf '\n%s: dry run — %s action(s) planned, %s already ok/skipped' "$app" "$linked" "$skipped"
else
	printf '\n%s: %s linked, %s already ok/skipped' "$app" "$linked" "$skipped"
fi
if [ "$conflicts" -gt 0 ]; then
	printf ', %s unresolved conflict(s)\n' "$conflicts" >&2
	printf 'Handle the conflicts manually, or re-run with --force to back them up.\n' >&2
	exit 1
fi
printf '\n'