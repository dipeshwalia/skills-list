"""Exercise the inventory and package builder against an isolated local fixture repository."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
REVIEWED = "1" * 40
MERGED = "2" * 40
LICENSE = "MIT License\n\nCopyright (c) 2026 Example Author\n"
SECTIONS = {
    "README.md": ("attribution",),
    "INVENTORY.md": ("sources", "requested", "supporting", "companions"),
    "skills/README.md": ("catalog",),
}


class BuildSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skills-export-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update({
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Build Test", "GIT_AUTHOR_EMAIL": "build-test@example.invalid",
            "GIT_COMMITTER_NAME": "Build Test", "GIT_COMMITTER_EMAIL": "build-test@example.invalid",
        })
        (self.root / "scripts").mkdir()
        for script in ("build-skills.py", "inventory.py", "upstream.py"):
            shutil.copy2(PROJECT / "scripts" / script, self.root / "scripts" / script)
        self.write("upstreams.json", json.dumps({
            "example": {"repository": "https://github.com/example/repo.git", "ref": "main"},
        }))
        self.write("upstreams/example/LICENSE", LICENSE)
        self.skill("one")
        self.skill("two")
        self.sources = [{
            "source": "example/repo",
            "author": "Example Author",
            "license": {"file": "LICENSE", "name": "MIT", "copyright": "2026 Example Author"},
            "reviewed": REVIEWED,
            "category": "Workflow",
            "skills": [
                {"name": "one", "purpose": "Explain one.", "requires": ["two"], "recommends": ["three"]},
                {"name": "two", "purpose": "Explain two.", "role": "supporting"},
            ],
        }]
        self.save_sources()
        for relative, sections in SECTIONS.items():
            markers = "".join(f"<!-- inventory:{name} -->\n<!-- /inventory:{name} -->\n\n" for name in sections)
            self.write(relative, f"Handwritten introduction.\n\n{markers}Handwritten notes.\n")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, env=self.env, check=True)
        self.record_merge(REVIEWED)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content)
        return path

    def skill(self, name, relative=None, revision=REVIEWED):
        relative = relative or f"upstreams/example/skills/{name}"
        self.write(f"{relative}/SKILL.md", (
            f"---\nname: {name}\ndescription: Explain {name} in a local test.\n"
            "disable-model-invocation: true\n---\n\n"
            f"# {name}\n\nRead /two and $two, then [the companion](../two/SKILL.md).\n"
            "Call the Skill tool with \"two\", then `two`. Label tickets `two`.\n"
            "The upstream example is https://example.com/two.\n"
            "Keep https://example.com/#/two and [docs](https://example.com/?next=/two).\n"
        ))
        self.write(f"{relative}/UPSTREAM.md", f"Original author: Example. Reviewed revision: {revision}. License: [MIT](../../LICENSE).\n")
        self.write(f"{relative}/LICENSE.upstream", LICENSE)
        return self.root / relative

    def select(self, *names, **fields):
        """Select plain requested skills with no companions."""
        self.sources[0]["skills"] = [{"name": name, "purpose": f"Explain {name}.", **fields} for name in names]
        self.save_sources()

    def save_sources(self):
        self.write("sources.json", json.dumps(self.sources, indent=2) + "\n")

    def record_merge(self, revision):
        subprocess.run(
            ["git", "commit", "-q", "--allow-empty", "-m", "Squashed 'upstreams/example/' content",
             "-m", f"git-subtree-dir: upstreams/example\ngit-subtree-split: {revision}"],
            cwd=self.root, env=self.env, check=True,
        )

    def build(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/build-skills.py"), *args],
            cwd=self.root.parent, env=self.env, text=True, capture_output=True, timeout=30,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def snapshot(self):
        result = {}
        for path in self.root.rglob("*"):
            if ".git" in path.relative_to(self.root).parts[:1]:
                continue
            metadata = path.lstat()
            if path.is_file():
                content = hashlib.sha256(path.read_bytes()).hexdigest()
            elif path.is_symlink():
                content = str(path.readlink())
            else:
                content = None
            result[str(path.relative_to(self.root))] = (
                stat.S_IMODE(metadata.st_mode), metadata.st_mtime_ns, content,
            )
        return result

    def test_export_uses_prefixed_names_and_preserves_resources_and_metadata(self):
        source = self.root / "upstreams/example/skills/one"
        self.write("upstreams/example/skills/one/assets/sample.bin", b"\x00\xff/two\x80")
        launcher = self.write("upstreams/example/skills/one/scripts/run.sh", "#!/bin/sh\nprintf '/two'\n")
        launcher.chmod(0o755)
        self.write("upstreams/example/skills/one/agents/openai.yaml", (
            'interface:\n  default_prompt: "Use $one and $two."\n'
            "policy:\n  allow_implicit_invocation: false\n"
        ))
        original = (source / "SKILL.md").read_bytes()

        self.build()

        exported = self.root / "skills/workflow-one"
        text = (exported / "SKILL.md").read_text()
        self.assertIn("name: workflow-one", text)
        self.assertIn("disable-model-invocation: true", text)
        self.assertIn("/workflow-two", text)
        self.assertIn("$workflow-two", text)
        self.assertIn("../workflow-two/SKILL.md", text)
        self.assertIn('Call the Skill tool with "workflow-two", then `workflow-two`. Label tickets `two`.', text)
        self.assertIn("https://example.com/two", text)
        self.assertIn("https://example.com/#/two", text)
        self.assertIn("https://example.com/?next=/two", text)
        self.assertIn("COLLECTION.md", text)
        self.assertIn("workflow-two", (exported / "COLLECTION.md").read_text())
        self.assertIn("LICENSE.upstream", (exported / "UPSTREAM.md").read_text())
        self.assertIn("## Collection packaging", (exported / "UPSTREAM.md").read_text())
        self.assertEqual((exported / "assets/sample.bin").read_bytes(), b"\x00\xff/two\x80")
        self.assertEqual((exported / "scripts/run.sh").read_bytes(), launcher.read_bytes())
        self.assertEqual(stat.S_IMODE((exported / "scripts/run.sh").stat().st_mode), 0o755)
        agent = (exported / "agents/openai.yaml").read_text()
        self.assertIn("$workflow-one and $workflow-two", agent)
        self.assertIn("allow_implicit_invocation: false", agent)
        self.assertEqual((exported / "LICENSE.upstream").read_bytes(), (source / "LICENSE.upstream").read_bytes())
        self.assertEqual((source / "SKILL.md").read_bytes(), original)
        self.build("--check")

    def test_attribution_tables_are_generated_between_markers(self):
        self.build()
        readme = (self.root / "README.md").read_text()
        self.assertIn(
            "| Example Author | [example/repo](https://github.com/example/repo) | "
            "[one](skills/workflow-one/SKILL.md), [two](skills/workflow-two/SKILL.md) | "
            "[MIT](upstreams/example/LICENSE) |", readme,
        )
        inventory = (self.root / "INVENTORY.md").read_text()
        self.assertIn(f"[`{REVIEWED}`](https://github.com/example/repo/commit/{REVIEWED})", inventory)
        self.assertIn("| `one` | `two` | `three` (not selected) |", inventory)
        self.assertIn(f"[Example Author · original](https://github.com/example/repo/tree/{REVIEWED}/skills/two)", inventory)
        catalog = (self.root / "skills/README.md").read_text()
        self.assertIn("## Workflow", catalog)
        self.assertIn("| Explain two. Supporting dependency. |", catalog)
        for path in SECTIONS:
            text = (self.root / path).read_text()
            self.assertTrue(text.startswith("Handwritten introduction.\n") and text.endswith("Handwritten notes.\n"))
        self.build("--check")

        self.write("README.md", readme.replace("Example Author |", "Someone Else |"))
        self.assertIn("README.md", self.build("--check", success=False).stderr)
        self.build()
        self.assertEqual((self.root / "README.md").read_text(), readme)
        self.write("README.md", "No markers here.\n")
        self.assertIn("inventory:attribution", self.build(success=False).stderr)

    def test_unreviewed_merge_blocks_publication_until_provenance_is_refreshed(self):
        self.build()
        self.record_merge(MERGED)
        before = self.snapshot()
        for args in ((), ("--check",)):
            with self.subTest(args=args):
                result = self.build(*args, success=False)
                self.assertIn(f"merged at {MERGED}", result.stderr)
                self.assertIn("Nothing was published", result.stderr)
                self.assertEqual(self.snapshot(), before)
        self.sources[0]["reviewed"] = MERGED
        self.save_sources()
        self.assertIn("does not name reviewed revision", self.build(success=False).stderr)
        for name in ("one", "two"):
            self.skill(name, revision=MERGED)
        self.build()
        self.assertIn(MERGED, (self.root / "INVENTORY.md").read_text())
        self.build("--check")

    def test_required_companions_and_supporting_roles_are_enforced(self):
        self.sources[0]["skills"] = self.sources[0]["skills"][:1]
        self.save_sources()
        result = self.build(success=False)
        self.assertIn("one requires two", result.stderr)
        self.assertIn("Recommendations stay optional", result.stderr)
        self.sources[0]["skills"] = [
            {"name": "one", "purpose": "Explain one."},
            {"name": "two", "purpose": "Explain two.", "role": "supporting"},
        ]
        self.save_sources()
        self.assertIn("two", self.build(success=False).stderr)
        for bad in ({"requires": ["one"]}, {"requires": ["two"], "recommends": ["two"]}, {"role": "optional"}):
            with self.subTest(bad=bad):
                self.sources[0]["skills"] = [{"name": "one", "purpose": "Explain one.", **bad}, {"name": "two", "purpose": "x"}]
                self.save_sources()
                self.build(success=False)

    def test_license_records_are_checked(self):
        self.write("upstreams/example/skills/two/LICENSE.upstream", "A paraphrased license.\n")
        self.assertIn("LICENSE.upstream differs", self.build(success=False).stderr)
        self.write("upstreams/example/skills/two/LICENSE.upstream", LICENSE)
        self.sources[0]["license"]["copyright"] = "2026 Someone Else"
        self.save_sources()
        self.assertIn("does not state", self.build(success=False).stderr)

    def test_hidden_folders_do_not_make_selected_skills_ambiguous(self):
        self.skill("one", "upstreams/example/skills/.cursor/one")
        self.build()
        names = {path.name for path in (self.root / "skills").iterdir() if path.is_dir()}
        self.assertEqual(names, {"workflow-one", "workflow-two"})

    def test_deselection_removes_generated_packages_and_preserves_originals(self):
        self.write("skills/my-original/SKILL.md", "My independently authored skill.\n")
        self.select("one", "two")
        self.build()
        self.select("one")
        self.build()
        self.assertTrue((self.root / "skills/workflow-one/SKILL.md").is_file())
        self.assertFalse((self.root / "skills/workflow-two").exists())
        self.assertEqual((self.root / "skills/my-original/SKILL.md").read_text(), "My independently authored skill.\n")
        self.assertFalse([path for path in (self.root / "skills").iterdir() if path.name.startswith(".build-")])
        self.build("--check")

    def test_unknown_selection_fails_before_any_generated_write(self):
        self.select("one", "missing")
        before = self.snapshot()
        self.build(success=False)
        self.assertEqual(self.snapshot(), before)

    def test_duplicate_names_and_alias_collisions_fail_before_writes(self):
        for collision in ("original", "alias"):
            with self.subTest(collision=collision):
                if collision == "original":
                    self.skill("one", "upstreams/example/alternate/one")
                    for folder in ("skills", "alternate"):
                        self.write(f"upstreams/example/{folder}/LICENSE", LICENSE)
                    first, second = dict(self.sources[0]), dict(self.sources[0])
                    first.update(source="example/repo/skills", skills=[{"name": "one", "purpose": "First."}])
                    second.update(source="example/repo/alternate", skills=[{"name": "one", "purpose": "Second."}])
                    self.sources = [first, second]
                else:
                    self.skill("flow-one")
                    self.sources[0]["source"] = "example/repo"
                    self.sources[0]["skills"] = [
                        {"name": "one", "category": "Work-flow", "purpose": "One."},
                        {"name": "flow-one", "category": "Work", "purpose": "Flow one."},
                    ]
                    self.sources = self.sources[:1]
                self.save_sources()
                before = self.snapshot()
                self.assertIn("Duplicate or ambiguous skill selection", self.build(success=False).stderr)
                self.assertEqual(self.snapshot(), before)

    def test_manual_generated_changes_are_not_overwritten(self):
        for change in ("edit", "add", "delete", "mode"):
            with self.subTest(change=change):
                self.build()
                path = self.root / "skills/workflow-one/SKILL.md"
                original = path.read_bytes()
                mode = stat.S_IMODE(path.stat().st_mode)
                extra = self.root / "skills/workflow-one/my-notes.md"
                if change == "edit":
                    path.write_text("My local edit.\n")
                elif change == "add":
                    extra.write_text("Do not delete my notes.\n")
                elif change == "delete":
                    path.unlink()
                else:
                    path.chmod(0o755)
                before = self.snapshot()
                self.build(success=False)
                self.assertEqual(self.snapshot(), before)
                if change == "add":
                    extra.unlink()
                else:
                    path.write_bytes(original)
                    path.chmod(mode)

    def test_check_is_read_only_and_detects_stale_outputs(self):
        before = self.snapshot()
        self.build("--check", success=False)
        self.assertEqual(self.snapshot(), before)
        self.build()
        before = self.snapshot()
        self.build("--check")
        self.assertEqual(self.snapshot(), before)
        source = self.root / "upstreams/example/skills/one/SKILL.md"
        source.write_text(source.read_text() + "\nAn upstream improvement.\n")
        before = self.snapshot()
        self.build("--check", success=False)
        self.assertEqual(self.snapshot(), before)
        self.build()
        self.assertIn("An upstream improvement.", (self.root / "skills/workflow-one/SKILL.md").read_text())
        self.build("--check")

    def test_hidden_and_tool_files_are_not_packaged_or_treated_as_edits(self):
        self.write("upstreams/example/skills/one/.DS_Store", b"finder")
        self.write("upstreams/example/skills/one/scripts/__pycache__/run.cpython.pyc", b"cache")
        self.build()
        package = self.root / "skills/workflow-one"
        self.assertFalse((package / ".DS_Store").exists())
        self.assertFalse((package / "scripts/__pycache__").exists())
        self.assertNotIn("DS_Store", (self.root / "skills/.generated.json").read_text())
        self.write("skills/workflow-one/.DS_Store", b"finder")
        self.write("skills/workflow-one/scripts/node_modules/tool/index.js", "module.exports = 1\n")
        self.build("--check")
        self.build()

    def test_other_hosts_trailing_slashes_and_malformed_upstreams(self):
        self.write("upstreams.json", json.dumps({
            "example": {"repository": "https://github.com/example/repo.git/", "ref": "main"},
            "elsewhere": {"repository": "https://gitlab.com/example/other.git", "ref": "main"},
        }))
        self.build()
        self.write("upstreams.json", json.dumps({"example": "https://github.com/example/repo.git"}))
        result = self.build(success=False)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_unselected_broken_skills_do_not_block_selected_ones(self):
        self.write("upstreams/example/skills/draft/SKILL.md", "---\nname: Draft Skill\n---\n")
        self.skill("three", "upstreams/example/skills/drafts/three")
        self.skill("three", "upstreams/example/skills/archive/three")
        self.build()
        for pick, message in (("draft", "expected a valid name"), ("three", "Ambiguous skill")):
            with self.subTest(pick=pick):
                self.select("one", pick)
                self.assertIn(message, self.build(success=False).stderr)

    def test_excluded_paths_are_left_out_and_recorded(self):
        self.write("upstreams/example/skills/one/scripts/test/fixture.txt", "A large test fixture.\n")
        self.select("one", exclude=["scripts/test"])
        self.build()
        package = self.root / "skills/workflow-one"
        self.assertFalse((package / "scripts/test").exists())
        self.assertIn("`scripts/test`", (package / "UPSTREAM.md").read_text())
        for bad in (["../escape"], ["LICENSE.upstream"], "scripts/test"):
            with self.subTest(exclude=bad):
                self.select("one", exclude=bad)
                self.build(success=False)

    @unittest.skipIf(os.name != "posix" or os.geteuid() == 0, "needs POSIX permissions as a non-root user")
    def test_failed_write_leaves_current_packages_intact(self):
        self.build()
        package = self.root / "skills/workflow-one/SKILL.md"
        before = package.read_bytes()
        source = self.root / "upstreams/example/skills/one/SKILL.md"
        source.write_text(source.read_text() + "\nAn upstream improvement.\n")
        skills = self.root / "skills"
        skills.chmod(0o555)
        self.addCleanup(skills.chmod, 0o755)
        self.build(success=False)
        skills.chmod(0o755)
        self.assertEqual(package.read_bytes(), before)
        self.build()
        self.build("--check")

    def test_existing_unmanaged_destination_is_not_overwritten(self):
        self.write("skills/workflow-one/SKILL.md", "An existing personal skill.\n")
        before = self.snapshot()
        self.build(success=False)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
