#!/usr/bin/env python3
"""Import and merge independently configured skill repositories with Git subtree."""

import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def git(*args, capture=False):
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE if capture else None,
    )


def read_sources():
    sources = json.loads((ROOT / "upstreams.json").read_text())
    if not isinstance(sources, dict):
        raise ValueError("upstreams.json must contain an object keyed by source name.")
    for name, source in sources.items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"Invalid source name: {name!r}. Use lowercase names with hyphens.")
        if not isinstance(source, dict) or set(source) != {"repository", "ref"}:
            raise ValueError(f"{name}: specify exactly repository and ref.")
        for key in ("repository", "ref"):
            value = source[key]
            if not isinstance(value, str) or not value.strip() or value.startswith("-"):
                raise ValueError(f"{name}: {key} must be a nonempty value, not an option.")
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List configured sources; does not contact remotes")
    sync = commands.add_parser("sync", help="Import a source or merge its latest changes")
    sync.add_argument("name")
    sync.add_argument("--dry-run", action="store_true", help="Print the Git command only")
    args = parser.parse_args()
    sources = read_sources()

    if args.command == "list":
        for name, source in sources.items():
            status = "present" if (ROOT / "upstreams" / name).exists() else "not imported"
            print(f"{name}: {status}; {source['repository']} ({source['ref']})")
        return

    if args.name not in sources:
        raise ValueError(f"Unknown source {args.name!r}; add it to upstreams.json first.")
    source = sources[args.name]
    prefix = f"upstreams/{args.name}"
    operation = "pull" if (ROOT / prefix).exists() else "add"
    command = [
        "subtree", operation, f"--prefix={prefix}",
        source["repository"], source["ref"], "--squash",
    ]
    print(shlex.join(["git", *command]), flush=True)
    if args.dry_run:
        return

    top = Path(git("rev-parse", "--show-toplevel", capture=True).stdout.strip()).resolve()
    if top != ROOT:
        raise ValueError("Initialize this folder as its own Git repository first.")
    git("rev-parse", "--verify", "HEAD", capture=True)
    if git("status", "--porcelain", "--untracked-files=all", capture=True).stdout:
        raise ValueError("Commit or stash local changes, including new files, before syncing.")
    if (ROOT / "upstreams").is_symlink() or (ROOT / prefix).is_symlink():
        raise ValueError("The upstream destination must be a normal directory, not a symlink.")

    git(*command)
    print(f"Finished {args.name}. Git subtree records the upstream commit in local history.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as error:
        print(
            "Git stopped. Check git status; resolve any merge conflicts before syncing again.",
            file=sys.stderr,
        )
        sys.exit(error.returncode)
