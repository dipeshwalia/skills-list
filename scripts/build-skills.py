#!/usr/bin/env python3
"""Build prefixed, installable skills from the reviewed editable upstream copies."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "skills/.generated.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.S)
NAME_FIELD = re.compile(r"^name:\s*(['\"]?)([a-z0-9-]+)\1\s*(?:#.*)?$", re.M)


def valid_name(value):
    return isinstance(value, str) and len(value) <= 64 and NAME.fullmatch(value)


def skill_name(path):
    text = (path / "SKILL.md").read_text()
    frontmatter = FRONTMATTER.match(text)
    fields = NAME_FIELD.findall(frontmatter[1]) if frontmatter else []
    if len(fields) != 1 or not valid_name(fields[0][1]):
        raise ValueError(f"{path}: expected a valid name in SKILL.md frontmatter.")
    name = fields[0][1]
    if path.name != name:
        raise ValueError(f"{path}: folder name must match skill name {name!r}.")
    return name


def repository_id(url):
    for prefix in ("https://github.com/", "git@github.com:"):
        if url.startswith(prefix):
            value = url[len(prefix):].removesuffix(".git").strip("/")
            if len(value.split("/")) == 2:
                return value.lower()
    raise ValueError(f"Unsupported repository URL for source selection: {url!r}")


def discover(path):
    if not path.is_dir() or path.is_symlink():
        raise ValueError(f"Source directory does not exist or is a symlink: {path}")
    found = {}
    for directory, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not (Path(directory) / d).is_symlink())
        if "SKILL.md" in files:
            package = Path(directory)
            name = skill_name(package)
            if name in found:
                raise ValueError(f"Ambiguous skill {name!r} under {path}.")
            found[name] = package
            dirs[:] = []
    return found


def selected_packages():
    upstreams = json.loads((ROOT / "upstreams.json").read_text())
    repositories = {}
    for key, upstream in upstreams.items():
        repo = repository_id(upstream["repository"])
        if repo in repositories:
            raise ValueError(f"Repository {repo!r} has more than one configured upstream.")
        repositories[repo] = ROOT / "upstreams" / key
    sources = json.loads((ROOT / "sources.json").read_text())
    if not isinstance(sources, list):
        raise ValueError("sources.json must contain an array.")
    selected, names = {}, set()
    for entry in sources:
        if not isinstance(entry, dict) or set(entry) - {"source", "category", "skills"} or not {"source", "category"} <= set(entry):
            raise ValueError("Each source must specify source, category, and optionally skills.")
        source = entry["source"]
        if not isinstance(source, str):
            raise ValueError("source must be owner/repo or owner/repo/sub/path.")
        parts = source.split("/")
        if len(parts) < 2 or any(not part or part in (".", "..") or "\\" in part for part in parts):
            raise ValueError(f"Invalid source: {source!r}")
        base = repositories.get("/".join(parts[:2]).lower())
        if base is None:
            raise ValueError(f"{source}: configure and import this repository in upstreams.json first.")
        path = base.joinpath(*parts[2:]) if len(parts) > 2 else base / "skills" if (base / "skills").is_dir() else base
        if not path.resolve().is_relative_to(base.resolve()):
            raise ValueError(f"Source escapes its upstream repository: {source}")
        category = entry["category"]
        if not isinstance(category, str):
            raise ValueError("category must be a string.")
        category = re.sub(r"[\s_]+", "-", category.strip().lower())
        if not valid_name(category):
            raise ValueError(f"Invalid category: {entry['category']!r}")
        found = discover(path)
        picks = entry.get("skills", sorted(found))
        if not isinstance(picks, list) or any(not isinstance(pick, str) for pick in picks):
            raise ValueError(f"{source}: skills must be an array of names.")
        if not found or not picks:
            raise ValueError(f"{source}: no skills selected.")
        for name in picks:
            if name not in found:
                raise ValueError(f"{source}: skill {name!r} was not found.")
            alias = f"{category}-{name}"
            if not valid_name(alias):
                raise ValueError(f"Invalid invocation name: {alias!r}")
            if alias in selected or name in names:
                raise ValueError(f"Duplicate or ambiguous skill selection: {name!r} ({alias}).")
            package = found[name]
            for required in ("UPSTREAM.md", "LICENSE.upstream"):
                if not (package / required).is_file():
                    raise ValueError(f"{package}: missing {required}; record source credits before building.")
            selected[alias] = (name, package)
            names.add(name)
    return dict(sorted(selected.items()))


def rewrite_references(text, aliases):
    names = "|".join(re.escape(name) for name in sorted(aliases, key=len, reverse=True))
    if not names:
        return text
    parts = re.split(r"([a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>\"']+)", text)
    for index in range(0, len(parts), 2):
        part = re.sub(r"(?<![\w./])\.\./(" + names + r")/", lambda m: "../" + aliases[m[1]] + "/", parts[index])
        parts[index] = re.sub(r"(?<![\w/])([/$])(" + names + r")(?![\w/-])", lambda m: m[1] + aliases[m[2]], part)
    return "".join(parts)


def desired_files(selected):
    aliases = {name: alias for alias, (name, _) in selected.items()}
    rows = "\n".join(f"| `{name}` | `/{alias}` |" for name, alias in sorted(aliases.items()))
    files = {}
    for alias, (name, source) in selected.items():
        destination = Path("skills") / alias
        if (source / "COLLECTION.md").exists():
            raise ValueError(f"{source}: COLLECTION.md is reserved for generated invocation guidance.")
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Skill resources must be regular files, not symlinks: {path}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise ValueError(f"Unsupported skill resource: {path}")
            relative = path.relative_to(source)
            data = path.read_bytes()
            if path.suffix.lower() == ".md" or (relative.parts[0] == "agents" and path.suffix.lower() in (".yaml", ".yml", ".toml")):
                text = rewrite_references(data.decode("utf-8"), aliases)
                if relative == Path("SKILL.md"):
                    frontmatter = FRONTMATTER.match(text)
                    header = NAME_FIELD.sub(f"name: {alias}", frontmatter[1], count=1)
                    note = "\nThis collection uses category-prefixed invocation names. When referring to another bundled skill, use its name from [the collection map](COLLECTION.md).\n\n"
                    text = "---\n" + header + "\n---\n" + note + text[frontmatter.end():].lstrip("\n")
                elif relative == Path("UPSTREAM.md"):
                    text = re.sub(r"\]\((?:\.\./)+LICENSE(?:\.md)?\)", "](LICENSE.upstream)", text)
                    text = text.rstrip() + (
                        "\n\n## Collection packaging\n\n"
                        "The source-change statements above describe the editable upstream copy. "
                        "This generated package changes its frontmatter name to the category-prefixed invocation, "
                        "updates explicit skill invocations and selected sibling links, and adds a "
                        "[collection name map](COLLECTION.md) with a reference to it in `SKILL.md`. "
                        "Portable license links point to `LICENSE.upstream`; the license text is unchanged.\n"
                    )
                data = text.encode("utf-8")
            files[(destination / relative).as_posix()] = (data, path.stat().st_mode & 0o777)
        collection = (
            f"# Collection invocation names\n\nInvoke this package as `/{alias}`.\n\n"
            f"Editable source: `{source.relative_to(ROOT).as_posix()}`. Edit that upstream copy, then run `python3 scripts/build-skills.py` from the repository root. Generated packages must not be edited directly.\n\n"
            "Use these names when the imported instructions refer to another selected skill:\n\n"
            "| Original name | Collection invocation |\n| --- | --- |\n" + rows + "\n"
        )
        files[(destination / "COLLECTION.md").as_posix()] = (collection.encode(), 0o644)
    return files


def fingerprint(data, mode):
    return {"sha256": hashlib.sha256(data).hexdigest(), "executable": bool(mode & 0o111)}


def read_state():
    if STATE.is_symlink():
        raise ValueError("The generated state file must not be a symlink.")
    if not STATE.exists():
        return {"version": 1, "packages": {}, "files": {}}
    state = json.loads(STATE.read_text())
    if not isinstance(state, dict) or set(state) != {"version", "packages", "files"} or state["version"] != 1:
        raise ValueError("Unsupported generated state file.")
    if not isinstance(state["packages"], dict) or not isinstance(state["files"], dict):
        raise ValueError("Invalid generated state file.")
    for alias in state["packages"]:
        if not valid_name(alias):
            raise ValueError("Invalid package name in generated state.")
    for path in state["files"]:
        parts = Path(path).parts
        if len(parts) < 3 or parts[0] != "skills" or parts[1] not in state["packages"] or ".." in parts:
            raise ValueError("Invalid managed path in generated state.")
    return state


def verify_managed(state, selected):
    skills = ROOT / "skills"
    if skills.is_symlink():
        raise ValueError("skills/ must not be a symlink.")
    for alias in selected:
        path = skills / alias
        if (path.exists() or path.is_symlink()) and alias not in state["packages"]:
            raise ValueError(f"Refusing to overwrite unmanaged skill directory: {path}")
    actual = set()
    for alias in state["packages"]:
        directory = skills / alias
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"Generated package was removed or replaced: {directory}")
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"Generated resource was replaced with a symlink: {path}")
            if path.is_file():
                relative = path.relative_to(ROOT).as_posix()
                actual.add(relative)
                recorded = state["files"].get(relative)
                if recorded != fingerprint(path.read_bytes(), path.stat().st_mode):
                    raise ValueError(f"Generated file has local edits: {relative}. Move the edit to its upstream source before rebuilding.")
    if actual != set(state["files"]):
        raise ValueError("Generated files were removed. Restore them before rebuilding.")


def build(check=False):
    selected = selected_packages()
    files = desired_files(selected)
    previous = read_state()
    verify_managed(previous, selected)
    state = {
        "version": 1,
        "packages": {alias: path.relative_to(ROOT).as_posix() for alias, (_, path) in selected.items()},
        "files": {path: fingerprint(data, mode) for path, (data, mode) in sorted(files.items())},
    }
    if check:
        if previous != state or not STATE.is_file():
            raise ValueError("Generated skills are stale. Run python3 scripts/build-skills.py.")
        print(f"Checked {len(selected)} generated skills.")
        return
    if previous == state and STATE.is_file():
        print(f"All {len(selected)} generated skills are current.")
        return
    # All inputs, destinations, and existing generated files are checked before any write.
    for alias in previous["packages"]:
        shutil.rmtree(ROOT / "skills" / alias)
    for relative, (data, mode) in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(f"Built {len(selected)} generated skills.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated output without changing files")
    args = parser.parse_args()
    try:
        build(args.check)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
