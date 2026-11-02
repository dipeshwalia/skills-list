"""Exercise upstream syncing against isolated local Git repositories."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]


class UpstreamSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skills-sync-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "personal"
        self.env = os.environ.copy()
        for key in list(self.env):
            if key.startswith("GIT_"):
                del self.env[key]
        self.env.update({
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Sync Test",
            "GIT_AUTHOR_EMAIL": "sync-test@example.invalid",
            "GIT_COMMITTER_NAME": "Sync Test",
            "GIT_COMMITTER_EMAIL": "sync-test@example.invalid",
            "GIT_TERMINAL_PROMPT": "0",
        })
        self.sources = {}
        for name in ("alpha", "beta", "unused"):
            source = self.base / name
            self.init(source)
            self.write(source, "SKILL.md", self.skill(name))
            self.write(source, "LICENSE", f"Original license for {name}\n")
            self.write(source, "obsolete.md", "Remove in a later revision.\n")
            self.commit(source, "Initial upstream")
            self.sources[name] = {"repository": str(source), "ref": "main"}
        self.init(self.repo)
        (self.repo / "scripts").mkdir()
        for name in ("upstream.py", "sync-upstreams.sh"):
            shutil.copy2(PROJECT / "scripts" / name, self.repo / "scripts" / name)
        self.write(self.repo, "README.md", "Personal repository\n")
        self.save_config()
        self.commit(self.repo, "Initial personal repository")

    def run_command(self, command, cwd, check=True):
        result = subprocess.run(
            command, cwd=cwd, env=self.env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30,
        )
        if check:
            self.assertEqual(result.returncode, 0, result.stdout)
        return result

    def git(self, directory, *args, check=True):
        return self.run_command(["git", *args], directory, check)

    def init(self, directory):
        directory.mkdir()
        self.git(directory, "init", "-b", "main")
        self.git(directory, "config", "commit.gpgsign", "false")
        self.git(directory, "config", "core.hooksPath", str(self.base / "no-hooks"))

    @staticmethod
    def write(directory, relative, text):
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    @staticmethod
    def skill(name):
        return (
            f"---\nname: {name}\ndescription: A local integration test skill.\n---\n"
            "local-value: original\n" + "Unchanged context.\n" * 12
            + "upstream-value: original\n"
        )

    def commit(self, directory, message):
        self.git(directory, "add", "-A")
        self.git(directory, "commit", "-m", message)

    def save_config(self):
        self.write(self.repo, "upstreams.json", json.dumps(self.sources, indent=2) + "\n")

    def sync(self, *args, check=True):
        # Deliberately run outside the personal repository.
        return self.run_command(
            [str(self.repo / "scripts/sync-upstreams.sh"), *args], self.base, check,
        )

    def head(self):
        return self.git(self.repo, "rev-parse", "HEAD").stdout.strip()

    def imported(self, name, filename="SKILL.md"):
        return self.repo / "upstreams" / name / filename

    def advance(self, name, value):
        source = Path(self.sources[name]["repository"])
        path = source / "SKILL.md"
        text = path.read_text()
        text = text[:text.index("upstream-value:")] + f"upstream-value: {value}\n"
        path.write_text(text)
        self.commit(source, f"Advance {name}: {value}")

    def fetch_head(self):
        path = self.repo / ".git/FETCH_HEAD"
        return path.read_bytes() if path.exists() else None

    def assert_unchanged_imports(self, before):
        for name, content in before.items():
            self.assertEqual(self.imported(name).read_text(), content)

    def test_named_import_and_default_or_explicit_all_from_another_directory(self):
        self.sync("alpha", "beta")
        for args, value in (((), "first"), (("--all",), "second")):
            with self.subTest(args=args):
                self.advance("alpha", value)
                self.advance("beta", value)
                self.sync(*args)
                for name in ("alpha", "beta"):
                    self.assertIn(f"upstream-value: {value}", self.imported(name).read_text())
                self.assertFalse((self.repo / "upstreams/unused").exists())
        before = self.head()
        self.sync()
        self.assertEqual(self.head(), before, "An up-to-date sync should not add commits")

    def test_all_does_not_import_configured_sources(self):
        before = self.head()
        self.sync()
        self.sync("--all")
        self.assertEqual(self.head(), before)
        self.assertFalse((self.repo / "upstreams").exists())
        self.assertIsNone(self.fetch_head())

    def test_invalid_selection_fails_before_updating_a_valid_source(self):
        self.sync("alpha", "beta")
        self.advance("alpha", "new")
        before = self.head(), self.fetch_head(), self.imported("alpha").read_text()
        for args in (("alpha", "missing"), ("--all", "alpha")):
            with self.subTest(args=args):
                self.assertNotEqual(self.sync(*args, check=False).returncode, 0)
                self.assertEqual(
                    (self.head(), self.fetch_head(), self.imported("alpha").read_text()), before,
                )

    def test_dry_run_does_not_fetch_commit_or_write_files(self):
        self.sync("alpha", "beta")
        self.advance("alpha", "not-fetched")

        def snapshot():
            return {
                str(path.relative_to(self.repo)): (
                    path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest(),
                )
                for path in self.repo.rglob("*") if path.is_file()
            }

        before = snapshot()
        self.sync("--dry-run")
        self.sync("unused", "--dry-run")
        self.assertEqual(snapshot(), before)

    def test_updates_preserve_custom_edits_and_credit_files(self):
        self.sync("alpha")
        path = self.imported("alpha")
        path.write_text(path.read_text().replace("local-value: original", "local-value: mine"))
        self.write(self.repo, "upstreams/alpha/UPSTREAM.md", "Original author and reviewed revision.\n")
        self.write(self.repo, "upstreams/alpha/LICENSE.upstream", "Portable original license.\n")
        self.commit(self.repo, "Customize alpha and retain credits")
        source = Path(self.sources["alpha"]["repository"])
        (source / "obsolete.md").unlink()
        self.write(source, "references/new.md", "New upstream supporting resource.\n")
        self.advance("alpha", "new")
        self.sync("alpha")
        self.assertIn("local-value: mine", path.read_text())
        self.assertIn("upstream-value: new", path.read_text())
        self.assertEqual(self.imported("alpha", "UPSTREAM.md").read_text(), "Original author and reviewed revision.\n")
        self.assertEqual(self.imported("alpha", "LICENSE.upstream").read_text(), "Portable original license.\n")
        self.assertFalse(self.imported("alpha", "obsolete.md").exists())
        self.assertEqual(self.imported("alpha", "references/new.md").read_text(), "New upstream supporting resource.\n")

    def test_sync_refreshes_packages_but_dry_run_does_not(self):
        self.write(self.repo, "scripts/build-skills.py", (
            "from pathlib import Path\n"
            "root = Path(__file__).resolve().parents[1]\n"
            "(root / 'generated.txt').write_bytes((root / 'upstreams/alpha/SKILL.md').read_bytes())\n"
        ))
        self.commit(self.repo, "Add package builder")
        self.sync("alpha")
        generated = self.repo / "generated.txt"
        self.assertEqual(generated.read_bytes(), self.imported("alpha").read_bytes())
        self.commit(self.repo, "Record initial generated package")
        self.advance("alpha", "updated")
        before = generated.read_bytes(), generated.stat().st_mtime_ns
        self.sync("alpha", "--dry-run")
        self.assertEqual((generated.read_bytes(), generated.stat().st_mtime_ns), before)
        self.sync("alpha")
        self.assertIn("upstream-value: updated", generated.read_text())
        self.assertEqual(generated.read_bytes(), self.imported("alpha").read_bytes())

    def test_package_failure_preserves_successful_upstream_import(self):
        self.write(self.repo, "scripts/build-skills.py", "raise SystemExit(2)\n")
        self.commit(self.repo, "Add failing package builder")
        result = self.sync("alpha", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.imported("alpha").exists())
        self.assertIn("skill package generation failed", result.stdout)
        self.assertEqual(self.git(self.repo, "status", "--porcelain").stdout, "")

    def test_configured_branch_and_pinned_tag_are_honored(self):
        alpha = Path(self.sources["alpha"]["repository"])
        beta = Path(self.sources["beta"]["repository"])
        self.git(alpha, "switch", "-c", "stable")
        self.git(beta, "tag", "v1")
        self.sources["alpha"]["ref"] = "stable"
        self.sources["beta"]["ref"] = "v1"
        self.save_config()
        self.commit(self.repo, "Track stable and pin v1")
        self.sync("alpha", "beta")
        self.git(alpha, "switch", "main")
        self.advance("alpha", "main-only")
        self.advance("beta", "after-tag")
        self.sync()
        for name in ("alpha", "beta"):
            self.assertIn("upstream-value: original", self.imported(name).read_text())
        self.git(alpha, "switch", "stable")
        self.advance("alpha", "stable-update")
        self.sync()
        self.assertIn("upstream-value: stable-update", self.imported("alpha").read_text())
        self.assertIn("upstream-value: original", self.imported("beta").read_text())

    def test_dirty_tracked_or_untracked_files_block_all_sources(self):
        self.sync("alpha", "beta")
        for name in ("alpha", "beta"):
            self.advance(name, "new")
        imports = {name: self.imported(name).read_text() for name in ("alpha", "beta")}
        before = self.head(), self.fetch_head()
        for relative in ("README.md", "scratch.txt"):
            with self.subTest(relative=relative):
                path = self.repo / relative
                original = path.read_bytes() if path.exists() else None
                path.write_text("Uncommitted work\n")
                self.assertNotEqual(self.sync(check=False).returncode, 0)
                self.assertEqual((self.head(), self.fetch_head()), before)
                self.assert_unchanged_imports(imports)
                self.assertEqual(path.read_text(), "Uncommitted work\n")
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)

    def test_unfinished_merge_with_clean_index_blocks_fetch(self):
        self.sync("alpha", "beta")
        self.git(self.repo, "switch", "-c", "pending")
        self.git(self.repo, "commit", "--allow-empty", "-m", "Pending merge")
        self.git(self.repo, "switch", "main")
        self.git(self.repo, "merge", "--no-ff", "--no-commit", "pending")
        self.assertEqual(self.git(self.repo, "status", "--porcelain").stdout, "")
        self.assertTrue((self.repo / ".git/MERGE_HEAD").exists())
        self.advance("alpha", "new")
        before = self.head(), self.fetch_head(), self.imported("alpha").read_text()
        self.assertNotEqual(self.sync(check=False).returncode, 0)
        self.assertEqual(
            (self.head(), self.fetch_head(), self.imported("alpha").read_text()), before,
        )

    def test_conflict_keeps_prior_success_and_stops_later_sources(self):
        self.sync("alpha", "beta", "unused")
        alpha = self.imported("alpha")
        alpha.write_text(alpha.read_text().replace("upstream-value: original", "upstream-value: mine"))
        self.write(self.repo, "upstreams/alpha/UPSTREAM.md", "Keep author credits.\n")
        self.write(self.repo, "upstreams/alpha/LICENSE.upstream", "Keep license.\n")
        self.commit(self.repo, "Customize alpha")
        for name in ("alpha", "beta", "unused"):
            self.advance(name, "remote")
        unused = self.imported("unused").read_text()
        # beta commits successfully; alpha conflicts; unused must not run.
        self.assertNotEqual(self.sync("beta", "alpha", "unused", check=False).returncode, 0)
        self.assertIn("upstream-value: remote", self.imported("beta").read_text())
        self.assertEqual(self.imported("unused").read_text(), unused)
        self.assertTrue((self.repo / ".git/MERGE_HEAD").exists())
        self.assertIn("<<<<<<<", alpha.read_text())
        self.assertEqual(self.imported("alpha", "UPSTREAM.md").read_text(), "Keep author credits.\n")
        self.assertEqual(self.imported("alpha", "LICENSE.upstream").read_text(), "Keep license.\n")


if __name__ == "__main__":
    unittest.main()
