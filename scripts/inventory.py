"""Resolve the skill inventory: selection, credits, reviewed revisions, and companions.

`resolve_inventory(root)` is the one place that reads sources.json and checks it against the
imported upstreams. Packaging and the generated attribution tables both use its result.
"""

from dataclasses import dataclass
import importlib.util
import json
import os
from pathlib import Path
import re
import sys


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.S)
NAME_FIELD = re.compile(r"^name:\s*(['\"]?)([a-z0-9-]+)\1\s*(?:#.*)?$", re.M)
REVISION = re.compile(r"[0-9a-f]{40}")
REQUIRED_FILES = {"SKILL.md", "UPSTREAM.md", "LICENSE.upstream"}
ROLES = ("requested", "supporting")
PROJECT_FIELDS = {"source", "author", "license", "reviewed", "category", "skills"}
SKILL_FIELDS = {"name", "purpose", "category", "role", "requires", "recommends", "exclude"}
LICENSE_FIELDS = {"file", "name", "copyright"}


@dataclass(frozen=True)
class Project:
    """An original author's project, credited as one unit."""

    source: str
    repository: str
    title: str
    url: str
    author: str
    license_name: str
    copyright: str
    license_file: Path
    reviewed: str
    upstream: str


@dataclass(frozen=True)
class Skill:
    """A selected skill with every fact its package and catalog entries need."""

    name: str
    alias: str
    category: str
    role: str
    purpose: str
    requires: tuple
    recommends: tuple
    excludes: tuple
    package: Path
    url: str
    project: Project


@dataclass(frozen=True)
class Inventory:
    projects: tuple
    skills: tuple


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
    """Return owner/repo for a GitHub URL, or None for hosts that sources.json cannot select."""
    for prefix in ("https://github.com/", "git@github.com:"):
        if url.startswith(prefix):
            value = url[len(prefix):].strip("/").removesuffix(".git")
            if len(value.split("/")) == 2:
                return value.lower()
    return None


def discover(path):
    """Map skill names to folders. Problems are reported only if a broken skill is selected."""
    if not path.is_dir() or path.is_symlink():
        raise ValueError(f"Source directory does not exist or is a symlink: {path}")
    found, problems = {}, {}
    for directory, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and not (Path(directory) / d).is_symlink())
        if "SKILL.md" in files:
            package = Path(directory)
            dirs[:] = []
            try:
                name = skill_name(package)
            except ValueError as error:
                problems.setdefault(package.name, str(error))
                continue
            if name in found:
                problems[name] = f"Ambiguous skill {name!r} under {path}."
            found.setdefault(name, package)
    return found, problems


def resolve_source_path(base, parts):
    """owner/repo/sub/path selects that folder; owner/repo selects its skills/ folder when present."""
    if len(parts) > 2:
        return base.joinpath(*parts[2:])
    if (base / "skills").is_dir():
        return base / "skills"
    return base


def load_upstream_helper():
    """Reuse the sync helper's upstreams.json validation and Git subtree lookups."""
    spec = importlib.util.spec_from_file_location("upstream_helper", Path(__file__).with_name("upstream.py"))
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def _text(value, what):
    if not isinstance(value, str) or not value.strip() or "\n" in value or "|" in value:
        raise ValueError(f"{what} must be a nonempty single line without '|'.")
    return value.strip()


def _names(value, what):
    if value is None:
        return ()
    if not isinstance(value, list) or len(set(value)) != len(value) or not all(valid_name(item) for item in value):
        raise ValueError(f"{what} must be a list of distinct skill names.")
    return tuple(value)


def _relative(value, what):
    path = Path(_text(value, what))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{what} must be a relative path inside its folder.")
    return path


def _project(root, record, repositories, helper):
    if not isinstance(record, dict) or set(record) - PROJECT_FIELDS or not PROJECT_FIELDS - {"category"} <= set(record):
        raise ValueError("Each sources.json record needs source, author, license, reviewed, and skills; category is optional.")
    source = _text(record["source"], "source")
    parts = source.split("/")
    if len(parts) < 2 or any(not part or part in (".", "..") or "\\" in part for part in parts):
        raise ValueError(f"Invalid source: {source!r}")
    upstream = repositories.get("/".join(parts[:2]).lower())
    if upstream is None:
        raise ValueError(f"{source}: configure and import this GitHub repository in upstreams.json first.")
    base = root / "upstreams" / upstream
    home, folder = base.joinpath(*parts[2:]), resolve_source_path(base, parts)
    if not all(path.resolve().is_relative_to(base.resolve()) for path in (home, folder)):
        raise ValueError(f"Source escapes its upstream repository: {source}")

    author = _text(record["author"], f"{source}: author")
    license = record["license"]
    if not isinstance(license, dict) or set(license) != LICENSE_FIELDS:
        raise ValueError(f"{source}: license needs file, name, and copyright.")
    license_file = home / _relative(license["file"], f"{source}: license file")
    license_name = _text(license["name"], f"{source}: license name")
    holder = _text(license["copyright"], f"{source}: license copyright")
    if not license_file.is_file():
        raise ValueError(f"{source}: license file {license_file.relative_to(root)} does not exist.")
    notice = license_file.read_text()
    if license_name not in notice or holder not in notice:
        raise ValueError(f"{source}: {license_file.relative_to(root)} does not state {license_name} and copyright {holder!r}.")

    reviewed = record["reviewed"]
    if not isinstance(reviewed, str) or not REVISION.fullmatch(reviewed):
        raise ValueError(f"{source}: reviewed must be a full 40-character commit SHA.")
    imported = helper.imported_revision(upstream)
    if imported is None:
        raise ValueError(f"upstreams/{upstream}: no Git subtree history found. Build from a Git clone that includes the import.")
    if imported != reviewed:
        raise ValueError(
            f"upstreams/{upstream} was merged at {imported}, but {source} was last reviewed at {reviewed}. "
            "Nothing was published. Review the merged changes and each selected skill's UPSTREAM.md, "
            f"then set \"reviewed\" to {imported} in sources.json before building."
        )

    repository = "/".join(parts[:2])
    title = repository if len(parts) == 2 else f"{parts[-1]} in {repository}"
    url = f"https://github.com/{repository}" + ("" if len(parts) == 2 else f"/tree/{reviewed}/{'/'.join(parts[2:])}")
    project = Project(
        source, repository, title, url, author, license_name, holder,
        license_file.relative_to(root), reviewed, upstream,
    )
    return project, folder


def _skill(root, entry, record, project, found, problems):
    if not isinstance(entry, dict) or set(entry) - SKILL_FIELDS or not {"name", "purpose"} <= set(entry):
        raise ValueError(
            f"{project.source}: each skill needs name and purpose; "
            "category, role, requires, recommends, and exclude are optional."
        )
    name = entry["name"]
    if not valid_name(name):
        raise ValueError(f"{project.source}: invalid skill name {name!r}.")
    if name in problems:
        raise ValueError(problems[name])
    if name not in found:
        raise ValueError(f"{project.source}: skill {name!r} was not found.")
    category = _text(entry.get("category", record.get("category")), f"{name}: category")
    prefix = re.sub(r"[\s_]+", "-", category.lower())
    alias = f"{prefix}-{name}"
    if not valid_name(prefix) or not valid_name(alias):
        raise ValueError(f"{name}: invalid category {category!r}.")
    role = entry.get("role", "requested")
    if role not in ROLES:
        raise ValueError(f"{name}: role must be requested or supporting.")
    purpose = _text(entry["purpose"], f"{name}: purpose")
    requires = _names(entry.get("requires"), f"{name}: requires")
    recommends = _names(entry.get("recommends"), f"{name}: recommends")
    if name in requires + recommends or set(requires) & set(recommends):
        raise ValueError(f"{name}: requires and recommends must name other skills, each in only one list.")
    excludes = entry.get("exclude", [])
    if not isinstance(excludes, list):
        raise ValueError(f"{name}: exclude must be a list of relative paths.")
    excludes = tuple(_relative(item, f"{name}: exclude") for item in excludes)
    if any(item.parts[0] in REQUIRED_FILES for item in excludes):
        raise ValueError(f"{name}: exclude cannot remove SKILL.md, UPSTREAM.md, or LICENSE.upstream.")

    package = found[name]
    folder = package.relative_to(root)
    for required in REQUIRED_FILES:
        if not (package / required).is_file():
            raise ValueError(f"{folder}: missing {required}; record source credits before building.")
    if (package / "LICENSE.upstream").read_bytes() != (root / project.license_file).read_bytes():
        raise ValueError(f"{folder}/LICENSE.upstream differs from {project.license_file}; copy the original license verbatim.")
    if project.reviewed not in (package / "UPSTREAM.md").read_text():
        raise ValueError(
            f"{folder}/UPSTREAM.md does not name reviewed revision {project.reviewed}. "
            "Refresh its provenance after reviewing the merged changes."
        )
    original = package.relative_to(root / "upstreams" / project.upstream).as_posix()
    url = f"https://github.com/{project.repository}/tree/{project.reviewed}/{original}"
    return Skill(name, alias, category, role, purpose, requires, recommends, excludes, package, url, project)


def _check_companions(skills):
    selected = {skill.name for skill in skills}
    missing = [f"{skill.name} requires {need}" for skill in skills for need in skill.requires if need not in selected]
    if missing:
        raise ValueError(
            "Incomplete selection: " + "; ".join(missing) + ". Select the required companions in "
            "sources.json, or remove the skills that need them. Recommendations stay optional."
        )
    supported = {need for skill in skills for need in skill.requires + skill.recommends}
    orphans = [skill.name for skill in skills if skill.role == "supporting" and skill.name not in supported]
    if orphans:
        raise ValueError(
            f"No selected skill requires or recommends these supporting skills: {', '.join(orphans)}. "
            "Mark them requested, or record the relationship in sources.json."
        )


def resolve_inventory(root):
    """Read sources.json, validate every fact it records, and return the selected skills."""
    root = Path(root).resolve()
    helper = load_upstream_helper()
    repositories = {}
    for key, upstream in helper.read_sources().items():
        repository = repository_id(upstream["repository"])
        if repository is None:
            continue  # Other hosts can still be synced; sources.json selects GitHub repositories only.
        if repository in repositories:
            raise ValueError(f"Repository {repository!r} has more than one configured upstream.")
        repositories[repository] = key
    records = json.loads((root / "sources.json").read_text())
    if not isinstance(records, list):
        raise ValueError("sources.json must contain an array of project records.")
    projects, skills, aliases, names = [], [], set(), set()
    for record in records:
        project, folder = _project(root, record, repositories, helper)
        if any(other.source.lower() == project.source.lower() for other in projects):
            raise ValueError(f"{project.source} appears more than once in sources.json.")
        entries = record["skills"]
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"{project.source}: skills must list at least one skill.")
        found, problems = discover(folder)
        projects.append(project)
        for entry in entries:
            skill = _skill(root, entry, record, project, found, problems)
            if skill.alias in aliases or skill.name in names:
                raise ValueError(f"Duplicate or ambiguous skill selection: {skill.name!r} ({skill.alias}).")
            aliases.add(skill.alias)
            names.add(skill.name)
            skills.append(skill)
    _check_companions(skills)
    return Inventory(tuple(projects), tuple(skills))


def catalog_sections(inventory):
    """Render the generated attribution tables, keyed by (file, section name)."""
    selected = {skill.name for skill in inventory.skills}

    def row(*cells):
        return "| " + " | ".join(cells) + " |"

    def table(header, rows):
        return "\n".join([row(*header), row(*["---"] * len(header)), *rows])

    def credit(skill):
        return f"[{skill.project.author} · original]({skill.url})"

    def companions(names):
        return ", ".join(f"`{name}`" + ("" if name in selected else " (not selected)") for name in names) or "—"

    attribution = table(
        ("Original author", "Original project", "Included skills", "License"),
        [
            row(
                project.author,
                f"[{project.title}]({project.url})",
                ", ".join(
                    f"[{skill.name}](skills/{skill.alias}/SKILL.md)"
                    for skill in sorted(inventory.skills, key=lambda skill: skill.name)
                    if skill.project == project
                ),
                f"[{project.license_name}]({project.license_file.as_posix()})",
            )
            for project in inventory.projects
        ],
    )
    sources = table(
        ("Source", "Original author", "License and copyright", "Reviewed upstream revision"),
        [
            row(
                f"[{project.title}]({project.url})",
                project.author,
                f"[{project.license_name} — {project.copyright}]({project.license_file.as_posix()})",
                f"[`{project.reviewed}`](https://github.com/{project.repository}/commit/{project.reviewed})",
            )
            for project in inventory.projects
        ],
    )
    header = ("Category", "Invocation / original skill", "Purpose", "Original author and source", "Package")

    def inventory_rows(role):
        return [
            row(skill.category, f"`/{skill.alias}` / `{skill.name}`", skill.purpose, credit(skill), f"[SKILL.md](skills/{skill.alias}/SKILL.md)")
            for skill in inventory.skills if skill.role == role
        ]

    relationships = table(
        ("Skill", "Requires (enforced)", "Recommends (optional)"),
        [
            row(f"`{skill.name}`", companions(skill.requires), companions(skill.recommends))
            for skill in inventory.skills if skill.requires or skill.recommends
        ],
    )
    catalog = "\n\n".join(
        f"## {category}\n\n" + table(
            ("Invocation", "Original skill", "Purpose", "Original source"),
            [
                row(
                    f"[`/{skill.alias}`]({skill.alias}/SKILL.md)",
                    f"`{skill.name}`",
                    skill.purpose + (" Supporting dependency." if skill.role == "supporting" else ""),
                    credit(skill),
                )
                for skill in inventory.skills if skill.category == category
            ],
        )
        for category in dict.fromkeys(skill.category for skill in inventory.skills)
    )
    return {
        ("README.md", "attribution"): attribution,
        ("INVENTORY.md", "sources"): sources,
        ("INVENTORY.md", "requested"): table(header, inventory_rows("requested")),
        ("INVENTORY.md", "supporting"): table(header, inventory_rows("supporting")),
        ("INVENTORY.md", "companions"): relationships,
        ("skills/README.md", "catalog"): catalog,
    }


if __name__ == "__main__":
    sys.exit("Run python3 scripts/build-skills.py; this module is imported by the builder.")
