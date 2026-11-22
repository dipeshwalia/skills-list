#!/usr/bin/env python3
"""Ask Gemini Neon a question through agy's Agent Client Protocol (ACP) server.

A run lives in one run directory:

    <run>/ws/          the staged workspace: the only files Neon may read
    <run>/prompt.txt   the question (you write it)
    <run>/result.json  the answer and what happened (ask writes it)
    <run>/progress.log one line per event (ask writes it, and echoes it to stderr)
    <run>/agy.log      agy's own log

Subcommands:

    new                         create a run directory; prints its path
    stage RUN --root DIR FILE…  copy files (paths relative to DIR) into RUN/ws
    ask RUN [--resume ID]       send RUN/prompt.txt to Neon; exit 0 only on SUCCESS
    start RUN [ask options]     run `ask` detached; an earlier result.json is archived
    wait RUN [--seconds N]      print new progress for up to N seconds, then the state:
                                exit 0 SUCCESS, 1 another final status, 2 still running

`ask` runs `agy acp` in RUN/ws, sets the model, thinking level and mode, and holds
Neon to reading files inside the workspace:

- Permission requests: reads inside the workspace are granted; everything else is
  refused. agy ends a turn after a refusal, so `ask` then sends at most two follow-up
  prompts asking Neon to answer from what it can read.
- Tripwire: agy runs some actions without asking (it has read files outside the
  workspace and run `ls` unasked). The moment a tool call that is not a read inside
  the workspace starts, `ask` stops agy and reports ABORTED. That usually beats the
  next model call, so the data rarely leaves, but it is not a guarantee: staging is
  the real protection.
"""
import argparse
import collections
import json
import os
import queue
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

MAX_STAGED_BYTES = 1_000_000
# File types that carry captures, data stores, secrets or bundles: never staged.
REFUSED_SUFFIXES = (".pcap", ".pcapng", ".cap", ".erf", ".parquet", ".db", ".sqlite", ".duckdb",
                    ".pem", ".key", ".p12", ".pfx", ".zip", ".tar", ".gz", ".tgz", ".zst", ".7z")
REFUSED_NAMES = (".env", "id_rsa", "id_ed25519", ".netrc", "credentials.json")
READ_TOOLS = (None, "read_file", "view_file", "list_dir")
PATH_KEYS = ("Path", "path", "AbsolutePath", "DirectoryPath", "SearchPath", "file", "File", "uri", "url")
CONTINUE = ("That action is not available in this consultation: {refused}. "
            "Read only files inside your working directory and run nothing. "
            "Answer the original question now from the prompt and the files you have read.")
MAX_CONTINUES = 2
CONFIG = ("model", "thought_level", "mode")


# ---------------------------------------------------------------------------
# new and stage
# ---------------------------------------------------------------------------

def cmd_new(_args):
    run = tempfile.mkdtemp(prefix="neon-run.", dir=os.environ.get("TMPDIR") or tempfile.gettempdir())
    os.mkdir(os.path.join(run, "ws"))
    print(run)
    return 0


def refusal(rel, path):
    name = os.path.basename(rel).lower()
    if os.path.isdir(path):
        return "is a directory; stage its files one by one"
    if not os.path.isfile(path):
        return "does not exist"
    if name.startswith(REFUSED_NAMES) or name.endswith(REFUSED_SUFFIXES):
        return "is a capture, data store, secret or archive"
    if os.path.getsize(path) > MAX_STAGED_BYTES:
        return f"is larger than {MAX_STAGED_BYTES:,} bytes; stage an excerpt instead"
    return None


def cmd_stage(args):
    root, ws = os.path.realpath(args.root), os.path.join(os.path.realpath(args.run), "ws")
    if not os.path.isdir(ws) or os.path.islink(ws):
        sys.exit(f"stage: {ws} is missing; create the run with `new`")
    problems = []
    for rel in args.files:
        src = os.path.realpath(os.path.join(root, rel))
        if os.path.commonpath([root, src]) != root or src == root:
            problems.append(f"{rel}: is outside {root}")
            continue
        why = refusal(rel, src) or refusal(os.path.relpath(src, root), src)
        if why:
            problems.append(f"{rel}: {why}")
            continue
        dst = os.path.join(ws, os.path.relpath(src, root))
        if os.path.commonpath([ws, os.path.realpath(dst)]) != ws:
            problems.append(f"{rel}: destination resolves outside the workspace")
            continue
        parent = dst
        while parent != ws and not os.path.islink(parent):
            parent = os.path.dirname(parent)
        if parent != ws:
            problems.append(f"{rel}: destination contains a symlink")
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"staged {os.path.relpath(src, root)}")
    for p in problems:
        print(f"refused {p}", file=sys.stderr)
    return 1 if problems else 0


# ---------------------------------------------------------------------------
# The ACP connection
# ---------------------------------------------------------------------------

class Acp:
    """A JSON-RPC 2.0 connection to `agy acp` over stdio.

    One thread reads agy's stdout, one writes its stdin, one drains its stderr, so a
    large prompt never deadlocks against agy's own output.
    """

    def __init__(self, cmd, cwd, on_notify, on_request, trace=None):
        self.trace = open(trace, "w", encoding="utf-8") if trace else None
        self.p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, encoding="utf-8", errors="replace",
                                  bufsize=1, start_new_session=True)
        self.on_notify, self.on_request = on_notify, on_request
        self.replies, self.next_id, self.lock = {}, 0, threading.Lock()
        self.outbox = queue.Queue()
        self.stderr = collections.deque(maxlen=50)
        self.closed = threading.Event()
        self.disconnected = threading.Event()
        self.close_lock = threading.Lock()
        self.threads = [threading.Thread(target=f, daemon=True) for f in (self._read, self._write, self._drain)]
        for t in self.threads:
            t.start()

    def _log(self, direction, text):
        if self.trace:
            self.trace.write(f"{direction} {text.rstrip()}\n")
            self.trace.flush()

    def _write(self):
        while True:
            msg = self.outbox.get()
            if msg is None:
                return
            line = json.dumps(msg)
            self._log(">", line)
            try:
                self.p.stdin.write(line + "\n")
                self.p.stdin.flush()
            except (OSError, ValueError):
                return

    def _drain(self):
        for line in self.p.stderr:
            self.stderr.append(line)

    def _read(self):
        try:
            for line in self.p.stdout:
                self._log("<", line)
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(msg, dict):
                    continue
                if msg.get("method") and msg.get("id") is not None:
                    try:
                        reply = {"result": self.on_request(msg["method"], msg.get("params") or {})}
                    except LookupError as e:
                        reply = {"error": {"code": -32601, "message": str(e)}}
                    except Exception as e:  # a handler bug must not kill the reader
                        reply = {"error": {"code": -32603, "message": f"{type(e).__name__}: {e}"}}
                    self.outbox.put({"jsonrpc": "2.0", "id": msg["id"], **reply})
                elif msg.get("method"):
                    try:
                        self.on_notify(msg["method"], msg.get("params") or {})
                    except Exception:
                        pass
                else:
                    with self.lock:
                        q = self.replies.pop(msg.get("id"), None)
                    if q:
                        q.put(msg)
        finally:  # agy exited or the stream broke: wake every waiting call
            with self.lock:
                self.disconnected.set()
                waiting, self.replies = list(self.replies.values()), {}
            for q in waiting:
                q.put({"error": {"message": f"agy acp exited (code {self.p.poll()})"}})

    def call(self, method, params, timeout):
        with self.lock:
            if self.closed.is_set() or self.disconnected.is_set():
                raise RuntimeError(f"{method}: connection closed")
            self.next_id += 1
            rid = self.next_id
            q = self.replies[rid] = queue.Queue()
        self.outbox.put({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        try:
            msg = q.get(timeout=max(0.1, timeout))
        except queue.Empty:
            with self.lock:
                self.replies.pop(rid, None)
            raise TimeoutError(f"{method} did not answer within {timeout:.0f}s")
        if msg.get("error") is not None:
            err = msg["error"]
            raise RuntimeError(f"{method}: {err.get('message')} {err.get('data') or ''}".strip())
        return msg.get("result") or {}

    def notify(self, method, params):
        self.outbox.put({"jsonrpc": "2.0", "method": method, "params": params})

    def close(self):
        with self.close_lock:
            if self.closed.is_set():
                return
            self.closed.set()
            self.outbox.put(None)
            # Stop the reader before closing stdin: a writer can hold its lock while
            # blocked on a full pipe, which would deadlock close before it sends TERM.
            for sig, wait in ((signal.SIGTERM, 10), (signal.SIGKILL, 5)):
                try:
                    os.killpg(self.p.pid, sig)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    self.p.wait(timeout=wait)
                    break
                except subprocess.TimeoutExpired:
                    continue
            # A reaped leader can leave descendants holding the inherited pipes.
            # Finish this process group before joining writers or closing their streams.
            try:
                os.killpg(self.p.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            for t in self.threads:
                if t is not threading.current_thread():
                    t.join(timeout=5)
            for stream in (self.p.stdin, self.p.stdout, self.p.stderr, self.trace):
                if stream:
                    try:
                        stream.close()
                    except OSError:
                        pass


# ---------------------------------------------------------------------------
# ask
# ---------------------------------------------------------------------------

def cmd_ask(args):
    run = os.path.realpath(args.run)
    ws = os.path.join(run, "ws")
    deadline = time.monotonic() + args.timeout
    t0 = time.monotonic()
    progress = open(os.path.join(run, "progress.log"), "a", encoding="utf-8")
    lock = threading.Lock()
    state = {"text": [], "thinking": False, "tools": {}, "refused": [], "outside": [], "abort": None,
             "collecting": False, "cancelling": False, "sid": None, "acp": None}
    result = {"status": "ERROR", "response": "", "session_id": args.resume,
              "model": args.model, "thought_level": args.thought, "mode": args.mode}

    def remaining(cap):
        return min(cap, deadline - time.monotonic())

    def say(event):
        line = f"[{time.monotonic() - t0:7.1f}s] {event}"
        print(line, file=sys.stderr, flush=True)
        progress.write(line + "\n")
        progress.flush()

    def inside(path):
        """True only for a plain local path that resolves inside the workspace."""
        if not isinstance(path, str) or not path.strip() or "://" in path or path.startswith("~") or "$" in path:
            return False
        real = os.path.realpath(path if os.path.isabs(path) else os.path.join(ws, path))
        return os.path.commonpath([ws, real]) == ws

    def paths_of(tc):
        found = [loc.get("path") for loc in tc.get("locations") or [] if isinstance(loc, dict)]
        for key in ("args", "rawInput"):
            a = tc.get(key)
            if isinstance(a, dict):
                found += [a[k] for k in PATH_KEYS if k in a]
        return found

    def contained(name, kind, paths):
        """A read of files inside the workspace: the only action Neon may take."""
        return kind == "read" and name in READ_TOOLS and bool(paths) and all(map(inside, paths))

    def merge_tool(update):
        with lock:
            tc = state["tools"].setdefault(update.get("toolCallId"), {"paths": []})
            tc.update({k: update[k] for k in ("name", "title", "kind", "status") if update.get(k)})
            tc["paths"] += [p for p in paths_of(update) if p not in tc["paths"]]
            return dict(tc)

    def trip(reason, paths):
        with lock:
            if state["abort"]:
                return
            state["abort"] = reason
            state["outside"] += [p for p in paths if not inside(p) and p not in state["outside"]]
        say(f"TRIPWIRE: {reason}; stopping agy")
        threading.Thread(target=state["acp"].close, daemon=True).start()

    def on_notify(method, params):
        if method != "session/update" or params.get("sessionId") != state["sid"]:
            return
        u = params.get("update") or {}
        kind = u.get("sessionUpdate")
        if not state["collecting"] or not kind:
            return
        if kind == "agent_message_chunk":
            content = u.get("content") or {}
            if content.get("type") == "text" and content.get("text"):
                with lock:
                    first = not state["text"]
                    state["text"].append(content["text"])
                if first:
                    say("answer started")
        elif kind == "agent_thought_chunk" and not state["thinking"]:
            state["thinking"] = True
            say("thinking")
        elif kind in ("tool_call", "tool_call_update") and u.get("toolCallId"):
            snapshot = merge_tool(u)
            if kind == "tool_call":
                say(f"tool: {snapshot.get('name') or snapshot.get('kind', '?')} {snapshot.get('title', '')}"[:200])
            # Pending calls may omit paths until a later update. Reject known unsafe
            # metadata immediately, and require complete containment once execution starts.
            unsafe = (snapshot.get("name") not in READ_TOOLS or
                      snapshot.get("kind") not in (None, "read") or
                      any(not inside(p) for p in snapshot["paths"]))
            executing = snapshot.get("status") in ("in_progress", "completed")
            if unsafe or (executing and not contained(snapshot.get("name"), snapshot.get("kind"), snapshot["paths"])):
                trip(f"Neon started {snapshot.get('name') or snapshot.get('kind')} {snapshot.get('title', '')}".strip(),
                     snapshot["paths"])

    def on_request(method, params):
        if method != "session/request_permission":
            raise LookupError(f"client does not support {method}")
        tc = params.get("toolCall") or {}
        known = merge_tool(tc)
        name, kind, paths = known.get("name"), known.get("kind"), known["paths"]
        label = f"{name or kind} {tc.get('title') or known.get('title', '')}".strip()
        if state["cancelling"] or params.get("sessionId") != state["sid"]:
            say(f"permission cancelled: {label}"[:200])
            return {"outcome": {"outcome": "cancelled"}}
        allow = contained(name, kind, paths)
        options = [o for o in params.get("options") or [] if isinstance(o, dict) and o.get("optionId")]
        want = ("allow_once",) if allow else ("reject_once", "reject_always")
        option = next((o for k in want for o in options if o.get("kind") == k), None)
        if not allow:
            with lock:
                state["refused"].append(label)
                state["outside"] += [p for p in paths if not inside(p) and p not in state["outside"]]
        outcome = ("granted" if allow else "refused") if option else "cancelled (no matching option)"
        say(f"permission {outcome}: {label}"[:200])
        return {"outcome": {"outcome": "selected", "optionId": option["optionId"]}} if option else {"outcome": {"outcome": "cancelled"}}

    def apply_config(sid, options):
        """Set model, thinking level and mode, then check all three in agy's final answer."""
        for key, value in zip(CONFIG, (args.model, args.thought, args.mode)):
            option = next((o for o in options if o.get("id") == key), None) or \
                next((o for o in options if o.get("category") == key), None)
            if option is None:
                raise RuntimeError(f"agy offers no {key} setting")
            reply = state["acp"].call("session/set_config_option",
                                      {"sessionId": sid, "configId": option["id"], "value": value}, timeout=remaining(60))
            options = reply.get("configOptions") or options
        for key, value in zip(CONFIG, (args.model, args.thought, args.mode)):
            current = next((o.get("currentValue") for o in options if o.get("id") == key or o.get("category") == key), None)
            if current != value:
                raise RuntimeError(f"agy kept {key}={current!r} instead of {value!r}")

    def on_sigterm(_sig, _frame):
        raise SystemExit("ask: stopped by SIGTERM")

    signal.signal(signal.SIGTERM, on_sigterm)
    acp = None
    try:
        if not os.path.isdir(ws) or os.path.islink(ws):
            raise RuntimeError(f"{ws} is missing or a symlink; create the run with `new`")
        with open(os.path.join(run, "prompt.txt"), encoding="utf-8") as f:
            prompt = f.read()
        if not prompt.strip():
            raise RuntimeError("prompt.txt is empty; write the consultation question first")
        acp = state["acp"] = Acp(["agy", "acp", "--log-file", os.path.join(run, "agy.log")],
                                 ws, on_notify, on_request, args.trace)
        init = acp.call("initialize", {"protocolVersion": 1, "clientCapabilities": {
            "fs": {"readTextFile": False, "writeTextFile": False}, "terminal": False}}, timeout=remaining(60))
        if init.get("protocolVersion") != 1:
            raise RuntimeError(f"agy speaks ACP version {init.get('protocolVersion')!r}, not 1")
        if args.resume:
            if not (init.get("agentCapabilities") or {}).get("loadSession"):
                raise RuntimeError("agy cannot resume sessions")
            state["sid"] = args.resume
            opened = acp.call("session/load", {"sessionId": args.resume, "cwd": ws, "mcpServers": []}, timeout=remaining(120))
        else:
            opened = acp.call("session/new", {"cwd": ws, "mcpServers": []}, timeout=remaining(120))
            state["sid"] = opened["sessionId"]
        sid = result["session_id"] = state["sid"]
        apply_config(sid, opened.get("configOptions") or [])
        say(f"session {sid}: {args.model} {args.thought}, {args.mode} mode; prompt sent")
        text, continues = prompt, 0
        while True:
            refused_before = len(state["refused"])
            state["collecting"] = True
            try:
                done = acp.call("session/prompt", {"sessionId": sid, "prompt": [{"type": "text", "text": text}]},
                                timeout=remaining(args.timeout))
            except TimeoutError:
                result.update(status="TIMEOUT", error=f"no answer within {args.timeout:.0f}s; turn cancelled")
                state["cancelling"] = True
                acp.notify("session/cancel", {"sessionId": sid})
                time.sleep(5)  # let agy stop its tools before the process is stopped
                break
            finally:
                state["collecting"] = False
            result["stop_reason"] = done.get("stopReason")
            answered = "".join(state["text"]).strip()
            new_refusals = state["refused"][refused_before:]
            if answered or done.get("stopReason") != "end_turn" or continues >= MAX_CONTINUES or not new_refusals:
                break
            continues += 1
            text = CONTINUE.format(refused="; ".join(new_refusals))
            say(f"turn ended with no answer after a refusal; follow-up {continues} of {MAX_CONTINUES}")
        result["continues"] = continues
        if result["status"] != "TIMEOUT":
            if "".join(state["text"]).strip() and result.get("stop_reason") == "end_turn":
                result["status"] = "SUCCESS"
            else:
                result["error"] = f"turn ended with stopReason={result.get('stop_reason')!r}" + \
                    ("" if "".join(state["text"]).strip() else " and no answer")
    except TimeoutError as e:
        result.update(status="TIMEOUT", error=str(e))
    except (Exception, SystemExit, KeyboardInterrupt) as e:  # every failure lands in the result
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        if acp:
            acp.close()
    if state["abort"]:
        result.update(status="ABORTED", error=state["abort"])
    with lock:
        result.update(response="".join(state["text"]), duration_seconds=round(time.monotonic() - t0, 1),
                      tool_calls=[dict(t) for t in state["tools"].values()], refused=list(state["refused"]),
                      outside_workspace=list(dict.fromkeys(
                          os.path.realpath(p if os.path.isabs(p) else os.path.join(ws, p)) if isinstance(p, str) else repr(p)
                          for p in state["outside"])),
                      agy_stderr="".join(acp.stderr if acp else [])[-2000:])
    out = os.path.join(run, "result.json")
    with open(out + ".tmp", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    os.replace(out + ".tmp", out)
    say(f"done: {result['status']}" + (f" ({result['error']})" if result.get("error") else ""))
    progress.close()
    return 0 if result["status"] == "SUCCESS" else 1


def cmd_start(args):
    run = os.path.realpath(args.run)
    if os.path.exists(os.path.join(run, "ask.pid")) and running(run):
        sys.exit("start: an ask is already running in this run; use wait")
    old = os.path.join(run, "result.json")
    if os.path.exists(old):
        n = 1
        while os.path.exists(os.path.join(run, f"result.{n}.json")):
            n += 1
        os.replace(old, os.path.join(run, f"result.{n}.json"))
        print(f"archived the earlier result as result.{n}.json")
    argv = [sys.executable, "-I", os.path.realpath(__file__), "ask"] + sys.argv[sys.argv.index("start") + 1:]
    with open(os.path.join(run, "ask.out"), "a", encoding="utf-8") as out:
        p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=out, start_new_session=True)
    with open(os.path.join(run, "ask.pid"), "w") as f:
        f.write(str(p.pid))
    print(f"started; follow it with: wait {run}")
    return 0


def running(run):
    try:
        pid = int(open(os.path.join(run, "ask.pid")).read().strip())
        os.kill(pid, 0)
    except (OSError, ValueError):
        return False
    try:  # a finished child stays a zombie until reaped; treat that as not running
        return os.waitpid(pid, os.WNOHANG) == (0, 0)
    except ChildProcessError:
        return True


def cmd_wait(args):
    run = os.path.realpath(args.run)
    log, mark = os.path.join(run, "progress.log"), os.path.join(run, ".wait-offset")
    offset = int(open(mark).read()) if os.path.exists(mark) else 0
    end = time.monotonic() + args.seconds
    while True:
        if os.path.exists(log):
            with open(log, encoding="utf-8") as f:
                f.seek(offset)
                chunk = f.read()
                offset = f.tell()
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()
            with open(mark, "w") as f:
                f.write(str(offset))
        result = os.path.join(run, "result.json")
        if os.path.exists(result) and not running(run):
            status = json.load(open(result, encoding="utf-8")).get("status")
            print(f"final status: {status}; read {result}")
            return 0 if status == "SUCCESS" else 1
        if not running(run) and not os.path.exists(result):
            print(f"ask is not running and wrote no result; see {os.path.join(run, 'ask.out')}")
            return 1
        if time.monotonic() >= end:
            print("still running; call wait again")
            return 2
        time.sleep(2)


def main():
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = a.add_subparsers(dest="command", required=True)
    sub.add_parser("new", help="create a run directory and print its path")
    s = sub.add_parser("stage", help="copy files into RUN/ws")
    s.add_argument("run")
    s.add_argument("--root", required=True, help="directory the file paths are relative to")
    s.add_argument("files", nargs="+")
    for name, text in (("ask", "send RUN/prompt.txt to Neon and write RUN/result.json"),
                       ("start", "run ask detached")):
        k = sub.add_parser(name, help=text)
        k.add_argument("run")
        k.add_argument("--resume", metavar="SESSION_ID", help="continue an earlier session in the same run")
        k.add_argument("--model", default="gemini-4-neon")
        k.add_argument("--thought", default="xhigh", help="thinking level: low, medium, high, xhigh")
        k.add_argument("--mode", default="default", help="agy mode; default sends permission requests to this client")
        k.add_argument("--timeout", type=float, default=1800, help="seconds for the whole consultation")
        k.add_argument("--trace", help="write every raw ACP message to this file (debugging)")
    w = sub.add_parser("wait", help="print new progress and report whether ask has finished")
    w.add_argument("run")
    w.add_argument("--seconds", type=float, default=30, help="longest wait before returning (default 30)")
    args = a.parse_args()
    return {"new": cmd_new, "stage": cmd_stage, "ask": cmd_ask, "start": cmd_start, "wait": cmd_wait}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
