"""Exercise categorized skill exports against isolated local source packages."""

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


class BuildSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skills-export-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        for script in ("build-skills.py", "upstream.py"):
            shutil.copy2(PROJECT / "scripts" / script, self.root / "scripts" / script)
        self.write("upstreams.json", json.dumps({
            "example": {"repository": "https://github.com/example/repo.git", "ref": "main"},
        }))
        self.sources = [{"source": "example/repo", "category": "Workflow", "skills": ["one", "two"]}]
        self.save_sources()
        self.skill("one")
        self.skill("two")
        self.write("skills/README.md", "My hand-written catalog.\n")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content)
        return path

    def skill(self, name, relative=None):
        relative = relative or f"upstreams/example/skills/{name}"
        self.write(f"{relative}/SKILL.md", (
            f"---\nname: {name}\ndescription: Explain {name} in a local test.\n"
            "disable-model-invocation: true\n---\n\n"
            f"# {name}\n\nRead /two and $two, then [the companion](../two/SKILL.md).\n"
            "Call the Skill tool with \"two\", then `two`. Label tickets `two`.\n"
            "The upstream example is https://example.com/two.\n"
            "Keep https://example.com/#/two and [docs](https://example.com/?next=/two).\n"
        ))
        self.write(f"{relative}/UPSTREAM.md", "Original author: Example. License: [MIT](../../LICENSE).\n")
        self.write(f"{relative}/LICENSE.upstream", "An exact test license notice.\n")
        return self.root / relative

    def save_sources(self):
        self.write("sources.json", json.dumps(self.sources, indent=2) + "\n")

    def build(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/build-skills.py"), *args],
            cwd=self.root.parent, text=True, capture_output=True, timeout=30,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def snapshot(self):
        result = {}
        for path in self.root.rglob("*"):
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

    def test_omitted_selection_discovers_canonical_skills_once(self):
        self.sources[0].pop("skills")
        self.save_sources()
        self.skill("hidden", "upstreams/example/.cursor/skills/hidden")
        self.build()
        names = {path.name for path in (self.root / "skills").iterdir() if path.is_dir()}
        self.assertEqual(names, {"workflow-one", "workflow-two"})

    def test_deselection_removes_generated_packages_and_preserves_originals(self):
        self.write("skills/my-original/SKILL.md", "My independently authored skill.\n")
        self.build()
        self.sources[0]["skills"] = ["one"]
        self.save_sources()
        self.build()
        self.assertTrue((self.root / "skills/workflow-one/SKILL.md").is_file())
        self.assertFalse((self.root / "skills/workflow-two").exists())
        self.assertEqual((self.root / "skills/my-original/SKILL.md").read_text(), "My independently authored skill.\n")
        self.assertEqual((self.root / "skills/README.md").read_text(), "My hand-written catalog.\n")
        self.assertFalse([path for path in (self.root / "skills").iterdir() if path.name.startswith(".build-")])
        self.build("--check")

    def test_unknown_selection_fails_before_any_generated_write(self):
        self.sources[0]["skills"] = ["one", "missing"]
        self.save_sources()
        before = self.snapshot()
        self.build(success=False)
        self.assertEqual(self.snapshot(), before)

    def test_duplicate_names_and_alias_collisions_fail_before_writes(self):
        for collision in ("original", "alias"):
            with self.subTest(collision=collision):
                if collision == "original":
                    self.skill("one", "upstreams/example/alternate/one")
                    self.sources = [
                        {"source": "example/repo/skills/one", "category": "Workflow"},
                        {"source": "example/repo/alternate/one", "category": "Writing"},
                    ]
                else:
                    self.skill("flow-one")
                    self.sources = [
                        {"source": "example/repo/skills/one", "category": "Work-flow"},
                        {"source": "example/repo/skills/flow-one", "category": "Work"},
                    ]
                self.save_sources()
                before = self.snapshot()
                self.build(success=False)
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
                self.sources[0]["skills"] = ["one", pick]
                self.save_sources()
                self.assertIn(message, self.build(success=False).stderr)

    def test_excluded_paths_are_left_out_and_recorded(self):
        self.write("upstreams/example/skills/one/scripts/test/fixture.txt", "A large test fixture.\n")
        self.sources[0]["exclude"] = ["scripts/test"]
        self.save_sources()
        self.build()
        package = self.root / "skills/workflow-one"
        self.assertFalse((package / "scripts/test").exists())
        self.assertIn("`scripts/test`", (package / "UPSTREAM.md").read_text())
        for bad in (["../escape"], ["LICENSE.upstream"], "scripts/test"):
            with self.subTest(exclude=bad):
                self.sources[0]["exclude"] = bad
                self.save_sources()
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
