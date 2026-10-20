"""scripts/campaign_keepalive.py and its wiring: the self-test, the scheduled task, and the SessionStart observer."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

REPO = Path(__file__).resolve().parents[2]
AUTO = REPO / ".conclave" / "automations"
spec = importlib.util.spec_from_file_location("office_run", AUTO / "run.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


class KeepAlive(unittest.TestCase):
    def test_the_keepalive_self_test_passes(self):
        result = subprocess.run([sys.executable, str(REPO / "scripts" / "campaign_keepalive.py"), "--self-test"],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-4000:])
        self.assertIn("self-test: 0 failed", result.stdout + result.stderr)

    def test_the_keepalive_runs_after_logon_and_hourly(self):
        task = run.load_tasks(str(AUTO / "tasks.json"))["office-claude-keepalive"]
        self.assertEqual(task["command"], ["python", "scripts/campaign_keepalive.py", "resurrect"])
        self.assertEqual(task["trigger"], {"at_logon_delay_minutes": 3, "every_minutes": 60})
        self.assertGreater(task["timeout_minutes"], 240)  # four hours of supervision plus margin

    def test_the_session_start_hook_observes_every_session(self):
        settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        commands = [h["command"] for entry in settings["hooks"]["SessionStart"] for h in entry["hooks"]]
        self.assertTrue(any("campaign_keepalive.py" in c and "'observe'" in c for c in commands), commands)

    def test_the_writer_model_is_configured(self):
        import tomllib
        with open(REPO / ".conclave" / "keepalive.toml", "rb") as fh:
            self.assertTrue(tomllib.load(fh)["writer"]["model"].startswith("claude-"))

    def test_every_launch_opens_no_console(self):
        text = (REPO / "scripts" / "campaign_keepalive.py").read_text(encoding="utf-8")
        calls = text.count("subprocess.run([") + text.count("subprocess.Popen(")
        self.assertGreaterEqual(text.count("creationflags=") + text.count('"git", "init"'), calls)


if __name__ == "__main__":
    unittest.main()
