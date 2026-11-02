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


def is_present(name):
    destination = ROOT / "upstreams" / name
    return destination.exists() or destination.is_symlink()


def require_clean_repository(names):
    top = Path(git("rev-parse", "--show-toplevel", capture=True).stdout.strip()).resolve()
    if top != ROOT:
        raise ValueError("Initialize this folder as its own Git repository first.")
    git("rev-parse", "--verify", "HEAD", capture=True)
    git_dir = Path(git("rev-parse", "--absolute-git-dir", capture=True).stdout.strip())
    for operation in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
        if (git_dir / operation).exists():
            raise ValueError("Finish the current Git merge, rebase, or cherry-pick before syncing.")
    if git("status", "--porcelain", "--untracked-files=all", capture=True).stdout:
        raise ValueError("Commit or stash local changes, including new files, before syncing.")
    if (ROOT / "upstreams").is_symlink() or any(
        (ROOT / "upstreams" / name).is_symlink() for name in names
    ):
        raise ValueError("Upstream destinations must be normal directories, not symlinks.")


def subtree_command(name, source):
    operation = "pull" if is_present(name) else "add"
    return [
        "subtree", operation, f"--prefix=upstreams/{name}",
        source["repository"], source["ref"], "--squash",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List configured sources; does not contact remotes")
    sync = commands.add_parser("sync", help="Import a source or merge its latest changes")
    sync.add_argument("names", nargs="*", help="Sources to sync; defaults to all imported sources")
    sync.add_argument("--all", action="store_true", help="Sync all already-imported sources")
    sync.add_argument("--dry-run", action="store_true", help="Print the Git command only")
    args = parser.parse_args()
    sources = read_sources()

    if args.command == "list":
        for name, source in sources.items():
            status = "present" if is_present(name) else "not imported"
            print(f"{name}: {status}; {source['repository']} ({source['ref']})")
        return

    if args.all and args.names:
        parser.error("Choose named sources or --all, not both.")
    unknown = [name for name in args.names if name not in sources]
    if unknown:
        raise ValueError(f"Unknown source(s): {', '.join(unknown)}; add them to upstreams.json first.")
    names = list(dict.fromkeys(args.names)) if args.names else [
        name for name in sources if is_present(name)
    ]
    if not args.names:
        for name in sources:
            if name not in names:
                print(f"Skipping {name}: not imported. Import with: python3 scripts/upstream.py sync {name}")
    if not names:
        print("No imported upstreams to sync.")
        return

    if args.dry_run:
        for name in names:
            print(shlex.join(["git", *subtree_command(name, sources[name])]))
        if (ROOT / "scripts/build-skills.py").is_file():
            print(shlex.join([sys.executable, str(ROOT / "scripts/build-skills.py")]))
        return

    require_clean_repository(names)
    changed = []
    for name in names:
        command = subtree_command(name, sources[name])
        print(shlex.join(["git", *command]), flush=True)
        before = git("rev-parse", "HEAD", capture=True).stdout.strip()
        try:
            git(*command)
        except subprocess.CalledProcessError:
            print(f"Stopped at {name}; remaining sources were not synced.", file=sys.stderr)
            if changed:
                print(f"Earlier updates remain committed: {', '.join(changed)}.", file=sys.stderr)
            raise
        if git("rev-parse", "HEAD", capture=True).stdout.strip() != before:
            changed.append(name)
        print(f"Finished {name}. Upstream revision is recorded in Git subtree history.")

    if changed:
        print(
            f"Updated: {', '.join(changed)}. Review skill changes and dependencies, then refresh "
            "INVENTORY.md, UPSTREAM.md, and portable license copies as needed. "
            "Reviewed revisions were not advanced automatically."
        )

    builder = ROOT / "scripts/build-skills.py"
    if builder.is_file():
        result = subprocess.run([sys.executable, str(builder)], cwd=ROOT)
        if result.returncode:
            merged = (
                f"Upstream merges for {', '.join(changed)} are committed"
                if changed else "No upstream changes were merged"
            )
            raise ValueError(
                f"{merged}, but skill package generation failed. "
                "Fix the reported source or package issue and run python3 scripts/build-skills.py."
            )
        print("Skill packages refreshed. Review and commit any generated changes.")


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
