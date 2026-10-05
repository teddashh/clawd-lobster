"""sync-all.sh against a temporary git repo and a local bare remote.

The script is copied into the temp repo and run from a directory full of
decoy files, so a shell-expanded glob cannot satisfy the test. Nothing
here touches the real home directory or any remote except the bare repo
under the temp directory.
"""
import os
import platform
import shutil
import socket
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_SRC = REPO_ROOT / "scripts" / "sync-all.sh"
GITIGNORE = ".env\n.env.*\nsecrets/\n*.enc\n"
HOST_NAMES = {platform.node(), socket.gethostname()}
HOST_NAMES.discard("")
# Git requires an author on the throwaway commits. This is the maintainer
# address, split so the source line is not one contiguous address.
AUTHOR_EMAIL = "ted" + "@" + "ted-h.com"


class SyncAllScriptTests(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory(prefix="sync-all-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        (self.home / "Documents" / "Workspace").mkdir(parents=True)
        (self.root / "git-template").mkdir()
        for name in (
            "decoy.md", "decoy.json", "decoy.py", "decoy.ps1", "decoy.sh",
            "decoy.toml", "decoy.yml", "decoy.yaml", "decoy.html",
        ):
            (self.root / name).write_text("decoy, not in any repo\n", encoding="utf-8")

        self.env = os.environ.copy()
        self.env["HOME"] = str(self.home)
        self.env["USERPROFILE"] = str(self.home)
        self.env["GIT_TERMINAL_PROMPT"] = "0"
        self.env["GIT_CONFIG_GLOBAL"] = os.devnull
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        self.env["GIT_TEMPLATE_DIR"] = str(self.root / "git-template")
        self.env["GIT_AUTHOR_NAME"] = "Ted Huang"
        self.env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
        self.env["GIT_COMMITTER_NAME"] = "Ted Huang"
        self.env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
        self.env.pop("CLAWD_MACHINE_ID", None)

        self.wrapper = self.root / "wrapper"
        self.wrapper_remote = self.root / "wrapper.git"
        self.sample = self.home / "Documents" / "Workspace" / "sample"
        self.sample_remote = self.root / "sample.git"
        self._init_repo(self.wrapper, self.wrapper_remote, {
            ".gitignore": GITIGNORE,
            "README.txt": "base\n",
        })
        scripts = self.wrapper / "scripts"
        scripts.mkdir()
        shutil.copy(SCRIPT_SRC, scripts / "sync-all.sh")
        self._git(self.wrapper, "add", "scripts/sync-all.sh")
        self._git(self.wrapper, "commit", "-m", "add sync script")
        self._git(self.wrapper, "push", "origin", "master")
        self._init_repo(self.sample, self.sample_remote, {
            ".gitignore": GITIGNORE,
            "notes.txt": "base\n",
        })

    def _run(self, args, cwd):
        result = subprocess.run(
            args, cwd=cwd, env=self.env, capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"{args} in {cwd}\n{result.stdout}\n{result.stderr}"
            )
        return result

    def _git(self, repo, *args):
        return self._run(["git", *args], repo)

    def _init_repo(self, path, bare, files):
        self._run(["git", "init", "--bare", "-b", "master", str(bare)], self.root)
        path.mkdir(parents=True, exist_ok=True)
        self._run(["git", "init", "-b", "master", str(path)], path)
        self._git(path, "config", "user.name", "Ted Huang")
        self._git(path, "config", "user.email", AUTHOR_EMAIL)
        self._git(path, "config", "commit.gpgsign", "false")
        for rel, content in files.items():
            dest = path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        self._git(path, "add", ".")
        self._git(path, "commit", "-m", "init")
        self._git(path, "remote", "add", "origin", str(bare))
        self._git(path, "push", "-u", "origin", "master")

    def _head(self, repo):
        return self._git(repo, "rev-parse", "HEAD").stdout.strip()

    def _remote_files(self, bare):
        result = self._run(
            ["git", "--git-dir", str(bare), "ls-tree", "-r", "--name-only", "master"],
            self.root,
        )
        return set(result.stdout.splitlines())

    def _remote_show(self, bare, path):
        return self._run(
            ["git", "--git-dir", str(bare), "show", f"master:{path}"],
            self.root,
        ).stdout

    def _sync(self):
        before = {
            "wrapper": self._head(self.wrapper),
            "sample": self._head(self.sample),
        }
        result = subprocess.run(
            ["bash", str(self.wrapper / "scripts" / "sync-all.sh")],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
        )
        log_path = self.wrapper / ".claude-memory" / "sync.log"
        log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        self.assertEqual(
            result.returncode, 0,
            f"stdout={result.stdout}\nstderr={result.stderr}\nlog={log_text}",
        )
        self.assertNotIn("did not match", result.stderr)
        self.assertIn("Sync finished", log_text)
        return before, log_text

    def _assert_no_host_name(self, repo):
        subject = self._git(repo, "log", "-1", "--format=%s").stdout.strip()
        diff = self._git(repo, "show", "--format=", "HEAD").stdout
        self.assertRegex(subject, r"^auto-sync \d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
        for name in HOST_NAMES:
            self.assertNotIn(name, subject)
            self.assertNotIn(name, diff)

    def test_no_matching_pattern_still_commits_and_pushes(self):
        # sample contains no Markdown, JSON, YAML, HTML, or script files,
        # so every safe glob misses. A tracked edit must still be committed
        # and pushed.
        (self.sample / "notes.txt").write_text("edited\n", encoding="utf-8")
        before, log_text = self._sync()
        self.assertEqual(self._head(self.wrapper), before["wrapper"])
        self.assertNotEqual(self._head(self.sample), before["sample"])
        changed = self._git(
            self.sample, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD",
        ).stdout.splitlines()
        self.assertEqual(changed, ["notes.txt"])
        self.assertEqual(self._remote_show(self.sample_remote, "notes.txt"), "edited\n")
        self.assertIn("PUSH sample: done", log_text)
        self.assertNotIn("PUSH wrapper: done", log_text)
        self._assert_no_host_name(self.sample)
        self.assertNotIn(".claude-memory/sync.log", self._remote_files(self.sample_remote))

    def test_some_patterns_add_matches_and_skip_the_rest(self):
        (self.sample / "notes.txt").write_text("tracked edit\n", encoding="utf-8")
        note = self.sample / "docs" / "deep" / "note.md"
        note.parent.mkdir(parents=True)
        note.write_text("hello\n", encoding="utf-8")
        (self.sample / "public.json").write_text('{"ok":true}\n', encoding="utf-8")
        (self.sample / "skip.c").write_text("int x;\n", encoding="utf-8")
        (self.sample / ".env").write_text("TOKEN=not-a-real-secret\n", encoding="utf-8")
        secret = self.sample / "secrets" / "token.json"
        secret.parent.mkdir()
        secret.write_text('{"token":"not-a-real-secret"}\n', encoding="utf-8")
        (self.wrapper / "docs").mkdir()
        (self.wrapper / "docs" / "hello.md").write_text("wrapper note\n", encoding="utf-8")
        (self.wrapper / "skip.c").write_text("int y;\n", encoding="utf-8")

        before, log_text = self._sync()
        self.assertNotEqual(self._head(self.sample), before["sample"])
        self.assertNotEqual(self._head(self.wrapper), before["wrapper"])
        sample_files = self._remote_files(self.sample_remote)
        self.assertIn("docs/deep/note.md", sample_files)
        self.assertIn("public.json", sample_files)
        self.assertNotIn("skip.c", sample_files)
        self.assertNotIn(".env", sample_files)
        self.assertNotIn("secrets/token.json", sample_files)
        self.assertEqual(self._remote_show(self.sample_remote, "notes.txt"), "tracked edit\n")
        self.assertEqual(
            self._remote_show(self.sample_remote, "docs/deep/note.md"), "hello\n",
        )
        wrapper_files = self._remote_files(self.wrapper_remote)
        self.assertIn("docs/hello.md", wrapper_files)
        self.assertNotIn("skip.c", wrapper_files)
        self.assertNotIn(".claude-memory/sync.log", wrapper_files)
        self.assertIn("PUSH sample: done", log_text)
        self.assertIn("PUSH wrapper: done", log_text)
        self._assert_no_host_name(self.sample)
        self._assert_no_host_name(self.wrapper)
        for name in HOST_NAMES:
            self.assertNotIn(name, log_text)

    def test_clean_tree_does_not_commit(self):
        before, _log = self._sync()
        self.assertEqual(self._head(self.wrapper), before["wrapper"])
        self.assertEqual(self._head(self.sample), before["sample"])
        self.assertEqual(self._remote_files(self.sample_remote), {
            ".gitignore", "notes.txt",
        })

    def test_only_non_matching_files_do_not_commit(self):
        (self.sample / "foo.c").write_text("int z;\n", encoding="utf-8")
        (self.sample / "bar.bin").write_bytes(b"\x00\x01")
        (self.sample / "token.env").write_text("TOKEN=not-a-real-secret\n", encoding="utf-8")
        before, log_text = self._sync()
        self.assertEqual(self._head(self.wrapper), before["wrapper"])
        self.assertEqual(self._head(self.sample), before["sample"])
        self.assertNotIn("PUSH sample: done", log_text)
        self.assertNotIn("PUSH wrapper: done", log_text)


class PowerShellBomTests(unittest.TestCase):

    def test_non_ascii_ps1_files_have_a_utf8_bom(self):
        found = False
        for path in REPO_ROOT.rglob("*.ps1"):
            if ".git" in path.parts:
                continue
            data = path.read_bytes()
            body = data[3:] if data.startswith(b"\xef\xbb\xbf") else data
            if any(byte > 127 for byte in body):
                found = True
                self.assertTrue(
                    data.startswith(b"\xef\xbb\xbf"),
                    f"{path} has non-ASCII text and no UTF-8 BOM",
                )
                text = data.decode("utf-8")
                self.assertTrue(text.startswith("\ufeff"))
                if path.name == "install.ps1":
                    self.assertIn("UTF-8 with a BOM", text)
            else:
                self.assertFalse(
                    data.startswith(b"\xef\xbb\xbf"),
                    f"{path} is ASCII and should not gain a BOM",
                )
        self.assertTrue(found)

    def test_editorconfig_keeps_ps1_utf8_bom(self):
        text = (REPO_ROOT / ".editorconfig").read_text(encoding="utf-8")
        self.assertIn("[*.ps1]", text)
        self.assertIn("charset = utf-8-bom", text)


if __name__ == "__main__":
    unittest.main()
