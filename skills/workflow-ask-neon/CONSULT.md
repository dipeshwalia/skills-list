# Neon consultation

You run one **staged consultation** with Gemini 4 Neon at extra-high reasoning, then report its answer. Neon reads only a scratch workspace you fill with the files the question needs, and answers a self-contained prompt you write.

The brief in your instructions is all you know about the task. When it lacks the question, or names files without a root to find them, stop and report what is missing: you cannot ask the user. When it names an earlier run directory and session id, this is a follow-up: reuse that run (step 3).

## The client

[`scripts/neon_acp.py`](scripts/neon_acp.py) drives `agy acp` over the Agent Client Protocol. It stages files, sets the model, thinking level and mode, grants reads inside the workspace, refuses every other action, and kills agy with a tripwire when Neon starts anything else. Its docstring has the details. Call it as `python3 -I <skill dir>/scripts/neon_acp.py`, where `<skill dir>` is the folder holding this file. `new` prints the run path fully resolved; copy it exactly into every later command, since shell variables do not survive between tool calls.

## 1. Create the run and stage the workspace

```sh
python3 -I <skill dir>/scripts/neon_acp.py new                       # prints the run path
python3 -I <skill dir>/scripts/neon_acp.py stage <run> --root <repo> src/a.rs docs/b.md
```

`stage` copies single files into `<run>/ws` and prints each staged path; use those exact paths in the prompt. It refuses directories, missing files, paths outside the root, symlinks to refused files, captures, data stores, keys, archives, and anything over 1 MB. It copies the files it accepts even when it refuses others, so resolve each refusal by staging the right files, an excerpt, or a fact in the prompt.

Whatever Neon reads goes to Google. Stage source, docs and synthetic fixtures. Leave customer, subscriber and network data (captures, baselines, oracle or evidence files, logs) and anything the brief keeps in-house where it is. For a review, write a scoped diff into the workspace yourself, naming the real range and only vetted paths, then read it before going on:

```sh
git -C <repo> diff <base>...HEAD -- src/a.rs docs/b.md > <run>/ws/change.diff
```

For a question the prompt fully explains, leave `<run>/ws` empty. `ask` checks the whole workspace before it starts and refuses anything `stage` would refuse, so files you write yourself follow the same rules.

Done when every file the question depends on is in `<run>/ws` and nothing else is.

## 2. Write the prompt

Write `<run>/prompt.txt` (UTF-8). Start it with `Consultation:` and include:

- the question, the established facts from the brief, and its constraints;
- every staged file by its printed relative path, each with one line on why it matters, naming functions rather than line numbers (Neon reads the files and cites exact lines itself). Neon may read only the files you list;
- the working rules: "Read only the files listed here, by their relative paths. Run no commands, search nothing, use no web or subagents, and change no files. Give the whole answer in your reply.";
- the output wanted: ranked findings or recommendations with file references, and stated uncertainty.

Describe customers, carriers and tickets generically unless the brief says to name them. Keep the working rules in every follow-up prompt.

Done when someone with only `<run>/ws` and this prompt could answer the question.

## 3. Ask

Check `command -v agy`. Start the consultation, then call `wait` until it reports a final status:

```sh
python3 -I <skill dir>/scripts/neon_acp.py start <run>          # follow-up: start <run> --resume <session_id>
python3 -I <skill dir>/scripts/neon_acp.py wait <run>           # repeat while it exits 2
```

`start` returns at once. Run each `wait` as its own foreground tool call, one after another, until it exits 0 or 1; it returns within about 100 seconds, well inside a default tool timeout, and loops of `wait` inside one call outlast it. `wait` prints each new progress line (`session …`, `thinking`, `tool: …`, `permission …`, `blocked by agy: …`, `TRIPWIRE: …`, `answer started`, `done: <status>`) and exits 0 for SUCCESS, 1 for another final status, 2 while Neon is still working.

An xhigh answer typically takes 5 to 15 minutes, and most of that is silence: no new lines between `thinking` and `answer started` for several minutes is normal. The client gives up at 30 minutes. A running `ask` holds `<run>/ask.lock`, so `wait` sees the moment it ends, however it ends.

Keep the defaults: model `gemini-4-neon`, thinking level `xhigh`, mode `default` (which sends permission requests to the client). When agy lacks the model or thinking level, the run ends in ERROR; report that instead of substituting another model or level.

For a follow-up, stage any extra files, write the new `prompt.txt`, and `start <run> --resume <session_id>` with the `session_id` from `result.json`; `--resume` accepts only that run's own session. `start` archives the earlier `result.json` as `result.<n>.json`.

## 4. Read the result

When `wait` exits 0 or 1, read `<run>/result.json`. Only `"status": "SUCCESS"` is a Neon answer.

| Status | Meaning | Action |
| --- | --- | --- |
| `SUCCESS` | Neon answered in `response` | Check `continues` and `refused`: a refused or blocked action means Neon wanted something you did not stage; note it when it weakens the answer |
| `ABORTED` | The tripwire fired: Neon started something other than a read inside the workspace (`error` names it; `outside_workspace` lists any paths, and is empty for commands), and the client killed agy | Report what Neon reached for. When it is a file you may stage under step 1, stage it or state the fact in the prompt, and try once more in a new run. Never stage sensitive data to satisfy it |
| `TIMEOUT` | No answer within 30 minutes; the turn was cancelled | Report it, with a narrower question to try |
| `ERROR` | agy missing, signed out, model unavailable, an unsafe workspace, or a turn that ended without an answer | Report `error`; for the cause, read `agy_stderr` in the result and `<run>/agy.log`. A sign-in failure needs the user to sign in through an interactive `agy` session |

The tripwire kills agy the moment the action is reported, which usually beats the next model call, but data may still have left. When it fires on a path that holds sensitive data, say so plainly.

## 5. Report

Your final message is all the caller receives, whatever the status. Give:

1. **Status**: the result status, and the error for anything but SUCCESS.
2. **Neon's answer**: its conclusions, ranked, with file references, attributed to Neon. Neon's links point into the run's `ws/` copy; give them as paths in the real repository instead. Keep its disagreements and uncertainty; mark anything you checked against the files as verified.
3. **Gaps**: what Neon could not see (`refused`, `outside_workspace`, files you left unstaged) and how that limits the answer.
4. **Follow-up handle**: the run path and `session_id`, so a later brief can continue the same consultation.
5. **Local copies**: the staged files remain under the run path, and agy keeps the session under `~/.gemini/antigravity-cli/brain/<session_id>` and `~/.gemini/antigravity-cli/conversations/<session_id>.db`. Say whether either holds anything sensitive.

Change no project files: you report, the caller decides.
