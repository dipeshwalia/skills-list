#!/usr/bin/env python3
"""Publish the reviewed inventory: category-prefixed skill packages and generated attribution tables."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "skills/.generated.json"
# Files that operating systems and tools create on their own; Git ignores them.
TOOL_FILES = {"Thumbs.db", "__pycache__", "node_modules"}


def load_inventory_module():
    """Load scripts/inventory.py, which owns selection, credit, review, and companion facts."""
    spec = importlib.util.spec_from_file_location("skill_inventory", Path(__file__).with_name("inventory.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


inventory_lib = load_inventory_module()


def unmanaged(relative):
    """Hidden entries and tool byproducts are never packaged or treated as edits."""
    return relative.suffix in (".pyc", ".pyo") or any(
        part.startswith(".") or part in TOOL_FILES for part in relative.parts
    )


def rewrite_references(text, aliases):
    names = "|".join(re.escape(name) for name in sorted(aliases, key=len, reverse=True))
    if not names:
        return text
    parts = re.split(r"([a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>\"']+)", text)
    for index in range(0, len(parts), 2):
        part = re.sub(r"(?<![\w./])\.\./(" + names + r")/", lambda m: "../" + aliases[m[1]] + "/", parts[index])
        part = re.sub(r"(?<![\w/])([/$])(" + names + r")(?![\w/-])", lambda m: m[1] + aliases[m[2]], part)
        # Quoted names in Skill tool instructions, such as: call the Skill tool with "grilling".
        quoted = re.compile(r"([\"'`])(" + names + r")\1")
        parts[index] = re.sub(
            r"[Ss]kill tool[^.\n]*",
            lambda span: quoted.sub(lambda m: m[1] + aliases[m[2]] + m[1], span[0]),
            part,
        )
    return "".join(parts)


def desired_files(inventory):
    aliases = {skill.name: skill.alias for skill in inventory.skills}
    rows = "\n".join(f"| `{name}` | `/{alias}` |" for name, alias in sorted(aliases.items()))
    files = {}
    for skill in inventory.skills:
        source, alias, excludes = skill.package, skill.alias, skill.excludes
        destination = Path("skills") / alias
        if (source / "COLLECTION.md").exists():
            raise ValueError(f"{source}: COLLECTION.md is reserved for generated invocation guidance.")
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if unmanaged(relative) or any(relative == item or item in relative.parents for item in excludes):
                continue
            if path.is_symlink():
                raise ValueError(f"Skill resources must be regular files, not symlinks: {path}")
            if path.is_dir():
                continue
            if not path.is_file():
                raise ValueError(f"Unsupported skill resource: {path}")
            data = path.read_bytes()
            if path.suffix.lower() == ".md" or (relative.parts[0] == "agents" and path.suffix.lower() in (".yaml", ".yml", ".toml")):
                text = rewrite_references(data.decode("utf-8"), aliases)
                if relative == Path("SKILL.md"):
                    frontmatter = inventory_lib.FRONTMATTER.match(text)
                    header = inventory_lib.NAME_FIELD.sub(f"name: {alias}", frontmatter[1], count=1)
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
                    if excludes:
                        listed = ", ".join(f"`{item.as_posix()}`" for item in excludes)
                        text += f"\nThis package omits these development-only upstream paths: {listed}.\n"
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


def render_catalogs(sections):
    """Return each catalog file's text with its generated sections replaced; handwritten text is kept."""
    rendered = {}
    for (relative, section), body in sections.items():
        path = ROOT / relative
        if relative not in rendered:
            if not path.is_file():
                raise ValueError(f"{relative} is missing; it holds generated attribution tables.")
            rendered[relative] = path.read_text()
        start, end = f"<!-- inventory:{section} -->", f"<!-- /inventory:{section} -->"
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        if len(pattern.findall(rendered[relative])) != 1:
            raise ValueError(f"{relative} needs exactly one generated section between `{start}` and `{end}`.")
        rendered[relative] = pattern.sub(lambda _: f"{start}\n\n{body}\n\n{end}", rendered[relative])
    return rendered


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
        if not inventory_lib.valid_name(alias):
            raise ValueError("Invalid package name in generated state.")
    for path in state["files"]:
        parts = Path(path).parts
        if len(parts) < 3 or parts[0] != "skills" or parts[1] not in state["packages"] or ".." in parts:
            raise ValueError("Invalid managed path in generated state.")
    return state


def verify_managed(state, aliases):
    skills = ROOT / "skills"
    if skills.is_symlink():
        raise ValueError("skills/ must not be a symlink.")
    for alias in aliases:
        path = skills / alias
        if (path.exists() or path.is_symlink()) and alias not in state["packages"]:
            raise ValueError(f"Refusing to overwrite unmanaged skill directory: {path}")
    actual = set()
    for alias in state["packages"]:
        directory = skills / alias
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"Generated package was removed or replaced: {directory}")
        for path in directory.rglob("*"):
            if unmanaged(path.relative_to(directory)):
                continue
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


def publish_packages(files, previous, state):
    # Stage every file first, so a failed write leaves the current packages untouched.
    staging, retired = ROOT / "skills/.build-staging", ROOT / "skills/.build-retired"
    for leftover in (staging, retired):
        if leftover.exists():
            shutil.rmtree(leftover)
    for relative, (data, mode) in files.items():
        path = staging / Path(relative).relative_to("skills")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)
    retired.mkdir(parents=True)
    for alias in previous["packages"]:
        os.replace(ROOT / "skills" / alias, retired / alias)
    for alias in state["packages"]:
        os.replace(staging / alias, ROOT / "skills" / alias)
    pending = STATE.with_name(STATE.name + ".tmp")
    pending.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    os.replace(pending, STATE)
    shutil.rmtree(retired)
    shutil.rmtree(staging)


def build(check=False):
    # The inventory validates selection, credits, reviewed revisions, and companions before any write.
    inventory = inventory_lib.resolve_inventory(ROOT)
    files = desired_files(inventory)
    catalogs = render_catalogs(inventory_lib.catalog_sections(inventory))
    previous = read_state()
    verify_managed(previous, [skill.alias for skill in inventory.skills])
    state = {
        "version": 1,
        "packages": {skill.alias: skill.package.relative_to(ROOT).as_posix() for skill in inventory.skills},
        "files": {path: fingerprint(data, mode) for path, (data, mode) in sorted(files.items())},
    }
    packages_current = previous == state and STATE.is_file()
    stale = sorted(path for path, text in catalogs.items() if (ROOT / path).read_text() != text)
    count = len(inventory.skills)
    if check:
        if not packages_current:
            raise ValueError("Generated skills are stale. Run python3 scripts/build-skills.py.")
        if stale:
            raise ValueError(f"Generated attribution tables are stale in {', '.join(stale)}. Run python3 scripts/build-skills.py.")
        print(f"Checked {count} generated skills and their attribution tables.")
        return
    if packages_current and not stale:
        print(f"All {count} generated skills and attribution tables are current.")
        return
    if not packages_current:
        publish_packages(files, previous, state)
    for path in stale:
        (ROOT / path).write_text(catalogs[path])
    print(f"Built {count} generated skills and their attribution tables.")


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
