"""Scheduler registration and command steps (onboarding executor).

Every subprocess call is mocked: these tests never touch the real crontab
or Task Scheduler of the machine that runs them.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from clawd_lobster.onboarding import executor, manifest

TASK = "clawd-lobster-evolve"
CWD = "/opt/clawd lobster"  # a space on purpose
JOB = ["/usr/bin/python3", "/opt/clawd lobster/scripts/evolve-tick.py"]
LINE = ("0 */2 * * * cd '/opt/clawd lobster' && /usr/bin/python3 "
        "'/opt/clawd lobster/scripts/evolve-tick.py' # clawd-lobster-evolve")


class FakeCrontab:
    """Stands in for the crontab binary and records every call."""

    def __init__(self, text=None, list_error=None, write_error=None):
        self.text = text  # None means "no crontab for this user"
        self.list_error = list_error
        self.write_error = write_error
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if args == ["crontab", "-l"]:
            if self.list_error:
                return subprocess.CompletedProcess(args, 1, "", self.list_error)
            if self.text is None:
                return subprocess.CompletedProcess(args, 1, "", "no crontab for tester\n")
            return subprocess.CompletedProcess(args, 0, self.text, "")
        if args == ["crontab", "-"]:
            if self.write_error:
                return subprocess.CompletedProcess(args, 1, "", self.write_error)
            self.text = kwargs["input"]
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError(f"unexpected command: {args}")

    def writes(self):
        return [kwargs["input"] for args, kwargs in self.calls if args == ["crontab", "-"]]


def register_cron(fake, schedule="0 */2 * * *", command=JOB):
    with patch.object(executor.subprocess, "run", fake):
        return executor._register_cron(TASK, schedule, command, CWD)


class TestCronRegistration(unittest.TestCase):

    def test_no_crontab_counts_as_empty(self):
        fake = FakeCrontab(text=None)
        r = register_cron(fake)
        self.assertTrue(r["ok"], r)
        self.assertTrue(r["changed"])
        self.assertEqual(fake.writes(), [LINE + "\n"])

    def test_runs_without_a_shell(self):
        fake = FakeCrontab(text=None)
        register_cron(fake)
        for args, kwargs in fake.calls:
            self.assertIsInstance(args, list)
            self.assertFalse(kwargs.get("shell", False))

    def test_appends_and_keeps_existing_entries(self):
        existing = "SHELL=/bin/sh\n0 1 * * * /usr/local/bin/backup\n"
        fake = FakeCrontab(text=existing)
        r = register_cron(fake)
        self.assertTrue(r["ok"], r)
        self.assertEqual(fake.writes(), [existing + LINE + "\n"])

    def test_existing_line_is_not_added_twice(self):
        fake = FakeCrontab(text="0 1 * * * /usr/local/bin/backup\n" + LINE + "\n")
        r = register_cron(fake)
        self.assertTrue(r["ok"], r)
        self.assertFalse(r["changed"])
        self.assertEqual(fake.writes(), [])

    def test_outdated_line_for_the_task_is_replaced_in_place(self):
        old = "0 */2 * * * cd /old && python scripts/evolve-tick.py # clawd-lobster-evolve"
        other = "*/5 * * * * /usr/local/bin/other # clawd-lobster-evolve-extra"
        fake = FakeCrontab(text=f"{old}\n0 1 * * * /usr/local/bin/backup\n{other}\n")
        r = register_cron(fake)
        self.assertTrue(r["ok"], r)
        self.assertEqual(fake.writes(),
                         [f"{LINE}\n0 1 * * * /usr/local/bin/backup\n{other}\n"])

    def test_unreadable_crontab_is_never_overwritten(self):
        fake = FakeCrontab(text="0 1 * * * /usr/local/bin/backup\n",
                           list_error="crontab: Permission denied\n")
        r = register_cron(fake)
        self.assertFalse(r["ok"])
        self.assertIn("crontab -l failed (exit 1)", r["error"])
        self.assertEqual(fake.writes(), [])

    def test_failed_write_is_reported(self):
        fake = FakeCrontab(text=None,
                           write_error="\"-\":1: bad minute\nerrors in crontab file, can't install.\n")
        r = register_cron(fake)
        self.assertFalse(r["ok"])
        self.assertIn("crontab - failed (exit 1)", r["error"])
        self.assertIn("bad minute", r["error"])

    def test_missing_crontab_program_is_reported(self):
        def missing(args, **kwargs):
            raise FileNotFoundError(2, "No such file or directory", args[0])
        r = register_cron(missing)
        self.assertFalse(r["ok"])
        self.assertIn("crontab -l failed", r["error"])

    def test_percent_signs_are_escaped(self):
        fake = FakeCrontab(text=None)
        register_cron(fake, command=["/usr/bin/date", "+%F"])
        self.assertIn("/usr/bin/date +\\%F # clawd-lobster-evolve", fake.writes()[0])

    def test_check_scheduler_matches_the_task_marker_only(self):
        cases = [(LINE + "\n", True), (None, False),
                 ("* * * * * /usr/local/bin/x # clawd-lobster-evolve-extra\n", False)]
        for text, expected in cases:
            with patch.object(executor, "_IS_WINDOWS", False), \
                 patch.object(executor.subprocess, "run", FakeCrontab(text=text)):
                self.assertEqual(executor.check_scheduler("evolve")["registered"], expected, text)


class TestWindowsRegistration(unittest.TestCase):

    def create(self, schedule, command, returncode=0, stderr=""):
        calls = []

        def fake(args, **kwargs):
            calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, returncode, "", stderr)

        with patch.object(executor.subprocess, "run", fake):
            r = executor._register_windows(TASK, schedule, command, r"D:\My Tools\clawd lobster")
        return r, calls

    def test_paths_with_spaces_stay_one_tr_argument(self):
        python = r"C:\Program Files\Python 3.12\python.exe"
        script = r"D:\My Tools\clawd lobster\scripts\evolve-tick.py"
        r, calls = self.create("0 */2 * * *", [python, script])
        self.assertTrue(r["ok"], r)
        self.assertEqual(len(calls), 1)
        args, kwargs = calls[0]
        self.assertEqual(args, ["schtasks", "/Create", "/TN", TASK,
                                "/TR", f'"{python}" "{script}"',
                                "/SC", "HOURLY", "/MO", "2", "/F"])
        self.assertFalse(kwargs.get("shell", False))

    def test_schedule_translation(self):
        self.assertEqual(executor._schtasks_schedule_args("*/30 * * * *"),
                         ["/SC", "MINUTE", "/MO", "30"])
        self.assertEqual(executor._schtasks_schedule_args("0 */2 * * *"),
                         ["/SC", "HOURLY", "/MO", "2"])
        self.assertEqual(executor._schtasks_schedule_args("15 3 * * *"),
                         ["/SC", "DAILY", "/ST", "03:15"])
        self.assertIsNone(executor._schtasks_schedule_args("not a cron line"))

    def test_unsupported_schedule_is_reported_without_running_schtasks(self):
        r, calls = self.create("every hour", ["python", "x.py"])
        self.assertFalse(r["ok"])
        self.assertIn("Unsupported cron expression", r["error"])
        self.assertEqual(calls, [])

    def test_schtasks_failure_is_reported(self):
        r, _ = self.create("*/30 * * * *", ["python", "x.py"],
                           returncode=1, stderr="ERROR: Access is denied.\n")
        self.assertFalse(r["ok"])
        self.assertIn("exit 1", r["error"])
        self.assertIn("Access is denied", r["error"])

    def test_check_scheduler_uses_an_argument_list(self):
        calls = []

        def fake(args, **kwargs):
            calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, 0, "", "")

        with patch.object(executor, "_IS_WINDOWS", True), \
             patch.object(executor.subprocess, "run", fake):
            self.assertTrue(executor.check_scheduler("heartbeat")["registered"])
        self.assertEqual(calls[0][0], ["schtasks", "/Query", "/TN", "clawd-lobster-heartbeat"])
        self.assertFalse(calls[0][1].get("shell", False))


class TestCommandStep(unittest.TestCase):

    def test_shell_pipelines_are_refused(self):
        step = {"command": {"unix": "echo '*/30 * * * * true' | crontab -",
                            "windows": "cmd /c echo hi > out.txt"}}
        with patch.object(executor.subprocess, "run") as run:
            ok, error = executor._run_command_step(step)
        self.assertFalse(ok)
        self.assertIn("without a shell", error)
        run.assert_not_called()

    def test_wrapper_dir_with_spaces_stays_one_argument(self):
        fake_file = "/opt/clawd lobster/clawd_lobster/onboarding/executor.py"
        wrapper = str(Path(fake_file).resolve().parent.parent.parent)
        calls = []

        def fake(args, **kwargs):
            calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, 0, "", "")

        step = {"command": "python -m pip install -e {{WRAPPER_DIR}}/skills/memory-server"}
        with patch.object(executor, "__file__", fake_file), \
             patch.object(executor.subprocess, "run", fake):
            ok, error = executor._run_command_step(step)
        self.assertTrue(ok, error)
        args, kwargs = calls[0]
        self.assertEqual(args, ["python", "-m", "pip", "install", "-e",
                                wrapper + "/skills/memory-server"])
        self.assertEqual(kwargs.get("cwd"), wrapper)
        self.assertFalse(kwargs.get("shell", False))

    def test_windows_split_keeps_quoted_paths_together(self):
        with patch.object(executor, "_IS_WINDOWS", True):
            args = executor._split_command(
                r'"C:\Program Files\Python 3.12\python.exe" -m pip install -e '
                r'"{{WRAPPER_DIR}}\skills\memory-server"')
        self.assertEqual(args, [r"C:\Program Files\Python 3.12\python.exe", "-m", "pip",
                                "install", "-e", r"{{WRAPPER_DIR}}\skills\memory-server"])

    def test_failed_command_is_reported(self):
        def fake(args, **kwargs):
            return subprocess.CompletedProcess(args, 2, "", "boom\n")

        with patch.object(executor.subprocess, "run", fake):
            ok, error = executor._run_command_step({"command": "python -c pass"})
        self.assertFalse(ok)
        self.assertEqual(error, "Command failed (exit 2): boom")


class TestScheduleStep(unittest.TestCase):

    def test_manifests_schedule_jobs_through_the_executor(self):
        manifests = {m["id"]: m for m in manifest.load_skill_manifests()}
        for skill_id in ("evolve", "heartbeat"):
            steps = manifests[skill_id]["onboarding"]["steps"]
            kinds = [(s["id"], s["kind"]) for s in steps]
            # Register first: the probe after it checks that the job exists
            self.assertEqual(kinds, [("register_cron", "schedule"), ("verify_script", "probe")])
            self.assertNotIn("command", steps[0])
        for m in manifests.values():
            for step in m["onboarding"].get("steps", []):
                self.assertNotIn("crontab", json.dumps(step.get("command", "")), m["id"])

    def test_schedule_step_registers_the_runtime_job(self):
        with patch.object(executor, "_IS_WINDOWS", False), \
             patch.object(executor, "register_scheduler",
                          return_value={"ok": True, "method": "cron"}) as reg:
            ok, error = executor._run_schedule_step("evolve")
        self.assertTrue(ok)
        self.assertIsNone(error)
        skill_id, schedule, command = reg.call_args.args
        self.assertEqual((skill_id, schedule), ("evolve", "0 */2 * * *"))
        self.assertEqual(command[0], sys.executable)
        self.assertTrue(command[1].endswith("evolve-tick.py"))
        self.assertTrue(Path(command[1]).is_file())

    def test_schedule_step_failure_carries_the_error(self):
        with patch.object(executor, "register_scheduler",
                          return_value={"ok": False, "method": "cron",
                                        "error": "crontab - failed (exit 1): bad minute"}):
            ok, error = executor._run_schedule_step("heartbeat")
        self.assertFalse(ok)
        self.assertIn("bad minute", error)

    def test_skill_without_a_schedule_fails_the_step(self):
        ok, error = executor._run_schedule_step("spec")
        self.assertFalse(ok)
        self.assertIn("No runtime schedule", error)

    def test_heartbeat_uses_its_powershell_script_on_windows(self):
        wrapper = Path(executor.__file__).resolve().parent.parent.parent
        with patch.object(executor, "_IS_WINDOWS", True):
            command = executor._job_command(wrapper, "scripts/heartbeat.sh")
        self.assertEqual(command[0], "powershell.exe")
        self.assertEqual(command[-1], str(wrapper / "scripts" / "heartbeat.ps1"))

    def test_missing_entrypoint_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(executor._job_command(Path(tmp), "scripts/missing.py"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
