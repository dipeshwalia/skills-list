"""Offline regression checks for staging, ACP events, and subprocess cleanup."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/workflow-ask-neon/scripts/neon_acp.py"
spec = importlib.util.spec_from_file_location("neon_acp", SCRIPT)
neon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(neon)


class NeonTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="neon-test-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "source"
        self.ws = self.base / "run/ws"
        self.root.mkdir()
        self.ws.mkdir(parents=True)

    def stage(self, *files):
        args = SimpleNamespace(root=str(self.root), run=str(self.ws.parent), files=files)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return neon.cmd_stage(args)

    def test_stage_copies_a_regular_file_with_its_relative_path(self):
        (self.root / "src").mkdir()
        (self.root / "src/main.py").write_text("print('example')\n")
        self.assertEqual(self.stage("src/main.py"), 0)
        self.assertEqual((self.ws / "src/main.py").read_bytes(), (self.root / "src/main.py").read_bytes())

    def test_stage_rejects_a_symlink_to_a_refused_source(self):
        (self.root / ".env").write_text("SYNTHETIC_SECRET=fixture\n")
        (self.root / "safe.txt").symlink_to(".env")
        self.assertEqual(self.stage("safe.txt"), 1)
        self.assertEqual(list(self.ws.iterdir()), [])

    def test_stage_rejects_escaping_destination_symlinks(self):
        (self.root / "src").mkdir()
        (self.root / "src/file.txt").write_text("replacement")
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "file.txt").write_text("preserve")
        (self.ws / "src").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.stage("src/file.txt"), 1)
        self.assertEqual((outside / "file.txt").read_text(), "preserve")

    def test_stage_rejects_an_existing_destination_symlink_inside_workspace(self):
        (self.root / "file.txt").write_text("replacement")
        (self.ws / "other.txt").write_text("preserve")
        (self.ws / "file.txt").symlink_to("other.txt")
        self.assertEqual(self.stage("file.txt"), 1)
        self.assertEqual((self.ws / "other.txt").read_text(), "preserve")

    def ask(self, updates=(), reject_thought=False, prompt="Consultation: explain a queue."):
        (self.ws.parent / "prompt.txt").write_text(prompt)
        args = SimpleNamespace(run=str(self.ws.parent), timeout=5, trace=None, resume=None,
                               model="gemini-4-neon", thought="xhigh", mode="default")
        configured = {}

        class FakeAcp:
            def __init__(self, _cmd, _cwd, on_notify, on_request, _trace):
                self.on_notify, self.stderr = on_notify, []
                self.on_request = on_request

            def call(self, method, params, timeout):
                options = [{"id": key, "currentValue": configured.get(key)} for key in neon.CONFIG]
                if method == "initialize":
                    return {"protocolVersion": 1}
                if method == "session/new":
                    return {"sessionId": "test-session", "configOptions": options}
                if method == "session/set_config_option":
                    value = "high" if reject_thought and params["configId"] == "thought_level" else params["value"]
                    configured[params["configId"]] = value
                    return {"configOptions": [{"id": key, "currentValue": configured.get(key)} for key in neon.CONFIG]}
                if method == "session/prompt":
                    for update in updates:
                        if "permission" in update:
                            self.on_request("session/request_permission", {
                                "sessionId": "test-session", "toolCall": update["permission"],
                                "options": [{"optionId": "allow", "kind": "allow_once"}],
                            })
                        else:
                            self.on_notify("session/update", {"sessionId": "test-session", "update": update})
                    self.on_notify("session/update", {"sessionId": "test-session", "update": {
                        "sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": "An answer."}}})
                    return {"stopReason": "end_turn"}
                raise AssertionError(method)

            def close(self):
                pass

        with patch.object(neon, "Acp", FakeAcp), patch.object(neon.signal, "signal"), \
                contextlib.redirect_stderr(io.StringIO()):
            code = neon.cmd_ask(args)
        return code, json.loads((self.ws.parent / "result.json").read_text()), configured

    def test_prompt_only_consultation_pins_neon_and_xhigh(self):
        code, result, configured = self.ask()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(configured, {"model": "gemini-4-neon", "thought_level": "xhigh", "mode": "default"})

    def test_empty_prompt_is_an_error(self):
        code, result, configured = self.ask(prompt=" \n")
        self.assertEqual(code, 1)
        self.assertIn("prompt.txt is empty", result["error"])
        self.assertEqual(configured, {})

    def test_unavailable_effort_fails_without_falling_back(self):
        code, result, _ = self.ask(reject_thought=True)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("instead of 'xhigh'", result["error"])

    def test_pending_read_can_receive_its_path_in_a_later_update(self):
        code, result, _ = self.ask([
            {"sessionUpdate": "tool_call", "toolCallId": "read", "kind": "read", "status": "pending"},
            {"sessionUpdate": "tool_call_update", "toolCallId": "read", "status": "in_progress",
             "locations": [{"path": "file.txt"}]},
        ])
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "SUCCESS")

    def test_outside_path_added_by_update_trips_the_boundary(self):
        outside = str(self.base / "outside.txt")
        code, result, _ = self.ask([
            {"sessionUpdate": "tool_call", "toolCallId": "read", "kind": "read", "status": "pending",
             "locations": [{"path": "file.txt"}]},
            {"sessionUpdate": "tool_call_update", "toolCallId": "read", "status": "in_progress",
             "rawInput": {"path": outside}},
        ])
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "ABORTED")
        self.assertIn(outside, result["outside_workspace"])

    def test_permission_metadata_is_retained_for_later_status_updates(self):
        code, result, _ = self.ask([
            {"sessionUpdate": "tool_call", "toolCallId": "read", "kind": "read", "status": "pending"},
            {"permission": {"toolCallId": "read", "kind": "read", "rawInput": {"path": "file.txt"}}},
            {"sessionUpdate": "tool_call_update", "toolCallId": "read", "status": "in_progress"},
        ])
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["refused"], [])
        self.assertEqual(result["tool_calls"][0]["paths"], ["file.txt"])

    def test_command_added_by_update_trips_the_boundary(self):
        code, result, _ = self.ask([
            {"sessionUpdate": "tool_call", "toolCallId": "call", "status": "pending"},
            {"sessionUpdate": "tool_call_update", "toolCallId": "call", "status": "in_progress", "kind": "execute"},
        ])
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "ABORTED")

    def connection(self, program):
        acp = neon.Acp([sys.executable, "-u", "-c", program], str(self.base), lambda *_: None, lambda *_: {})
        self.addCleanup(acp.close)
        return acp

    def test_request_after_eof_fails_immediately(self):
        acp = self.connection("pass")
        self.assertTrue(acp.disconnected.wait(5))
        started = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, "connection closed"):
            acp.call("session/prompt", {}, timeout=30)
        self.assertLess(time.monotonic() - started, 1)

    def test_close_terminates_a_child_with_a_full_input_pipe(self):
        acp = self.connection("import time; time.sleep(60)")
        self.close_with_full_pipe(acp)

    def test_close_terminates_descendants_that_keep_the_input_pipe_open(self):
        ready = self.base / "descendant-ready"
        acp = self.connection(
            "import os, signal, time\n"
            "if os.fork() == 0:\n"
            "    signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "    open('descendant-ready', 'w').close()\n"
            "time.sleep(60)\n"
        )
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(ready.exists())
        self.close_with_full_pipe(acp)

    def close_with_full_pipe(self, acp):
        acp.notify("large", {"text": "x" * 1_000_000})
        time.sleep(0.1)
        closer = threading.Thread(target=acp.close, daemon=True)
        closer.start()
        closer.join(5)
        if closer.is_alive():
            # Release the synthetic child if the regression returns, so the suite cannot hang.
            os.killpg(acp.p.pid, signal.SIGKILL)
            closer.join(5)
            self.fail("close blocked on the full input pipe")
        self.assertIsNotNone(acp.p.poll())


if __name__ == "__main__":
    unittest.main()
