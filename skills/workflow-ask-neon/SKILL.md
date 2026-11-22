---
name: workflow-ask-neon
description: Ask Gemini Neon (xhigh reasoning, through the Antigravity CLI) for a second opinion, review, or analysis when the user says "ask neon" or wants Neon's view. Runs in a background subagent that sees none of the conversation, so pass a self-contained brief as the argument - the question, facts established so far, the repository root and the files Neon should read, and the user's constraints.
argument-hint: "<brief: question, established facts, repo root and files to read, constraints>"
context: fork
agent: general-purpose
background: true
---

# Ask Neon

You run one **staged consultation** with Gemini 4 Neon at extra-high reasoning, then report its answer. Stage the files the question needs in a scratch workspace, and give Neon a self-contained prompt that limits its reads to those files.

On hosts that ignore the fork/background metadata, delegate this workflow to a fresh background subagent with only the brief when supported. Otherwise run it in the current agent and pass Neon the same self-contained prompt.

## The brief

$ARGUMENTS

This brief is all you know about the task. If no brief appears above, build one from the current task. When it lacks the question, or names files without a root to find them, stop and return what is missing: you cannot ask the user. When it names an earlier run directory and session id, this is a follow-up: reuse that run (step 3).

## The client

[`scripts/neon_acp.py`](scripts/neon_acp.py) drives `agy acp` over the Agent Client Protocol. It stages files, sets the model, thinking level and mode, grants reads inside the workspace, refuses every other action, and stops agy with a tripwire when Neon starts anything else. Its docstring has the details. Call it as `python3 -I <this skill's directory>/scripts/neon_acp.py`, and copy the printed run path into every later command: shell variables do not survive between tool calls.

## 1. Create the run and stage the workspace

```sh
python3 -I …/neon_acp.py new                                   # prints the run path
python3 -I …/neon_acp.py stage <run> --root <repo> src/a.rs docs/b.md
```

`stage` copies single files, keeping their paths relative to `--root`, into `<run>/ws`. It refuses directories, missing files, paths outside the root, captures, data stores, keys, archives, and anything over 1 MB; resolve each refusal by staging the right files, an excerpt, or a fact in the prompt.

Whatever Neon reads goes to Google. Stage source, docs and synthetic fixtures. Leave customer, subscriber and network data (captures, baselines, oracle or evidence files, logs) and anything the brief's data rules keep in-house where it is. For a review, write a scoped diff into the workspace yourself, naming the real range and only vetted paths, then read it before going on:

```sh
git -C <repo> diff <base>...HEAD -- src/a.rs docs/b.md > <run>/ws/change.diff
```

Done when every file the question depends on is in `<run>/ws` and nothing else is.

For a question fully explained in the prompt, leave `<run>/ws` empty and skip staging.

## 2. Write the prompt

Write `<run>/prompt.txt` (UTF-8). Start it with `Consultation:` and include:

- the question, the established facts from the brief, and its constraints;
- every staged file by its relative path, each with one line on why it matters. Neon has no search tool, so it reads exactly the paths you list;
- the working rules: "Read only the files listed here, by their relative paths. Run no commands, search nothing, use no web or subagents, and change no files. Give the whole answer in your reply.";
- the output wanted: ranked findings or recommendations with file references, and stated uncertainty.

Describe customers, carriers and tickets generically unless the brief says to name them.

Done when someone with only `<run>/ws` and this prompt could answer the question.

## 3. Ask

Check `command -v agy`. Start the consultation, then call `wait` until it reports a final status:

```sh
python3 -I …/neon_acp.py start <run>                     # follow-up: start <run> --resume <session_id>
python3 -I …/neon_acp.py wait <run>                      # repeat while it exits 2 ("still running")
```

`wait` prints each new progress line (`thinking`, `tool: …`, `permission …`, `answer started`, `done: <status>`) and returns within about 30 seconds: exit 0 for SUCCESS, 1 for another final status, 2 while Neon is still working. An xhigh answer can take several minutes; the client gives up at 30.

Keep the defaults: model `gemini-4-neon`, thinking level `xhigh`, mode `default` (which sends permission requests to the client). When agy lacks the model or thinking level, the run ends in ERROR; report that instead of substituting another model or level. For a follow-up, write the new `prompt.txt` first; `start` archives the earlier `result.json` as `result.<n>.json`.

## 4. Read the result

Read `<run>/result.json`. Only `"status": "SUCCESS"` is a Neon answer.

| Status | Meaning | Action |
| --- | --- | --- |
| `SUCCESS` | Neon answered in `response` | Check `continues` and `refused`: a refused action means Neon wanted something you did not stage; note it when it weakens the answer |
| `ABORTED` | The tripwire fired: Neon started something other than a read inside the workspace (`error` names it, `outside_workspace` lists the paths), and the client stopped agy | Stage the missing files or state the fact in the prompt, then try once more in a new run. Report what Neon reached for either way |
| `TIMEOUT` | No answer within 30 minutes; the turn was cancelled | Report it, with a narrower question to try |
| `ERROR` | agy missing, signed out, model unavailable, or a turn that ended without an answer | Report `error`. A sign-in failure needs the user to sign in through an interactive `agy` session |

The tripwire stops agy the moment the action starts, which usually beats the next model call, but data may still have left. When it fires on a path that holds sensitive data, say so plainly.

## 5. Report

Your final message is all the caller receives. Give:

1. **Status**: the result status, and the error for anything but SUCCESS.
2. **Neon's answer**: its conclusions, ranked, with file references, attributed to Neon. Keep its disagreements and uncertainty; mark anything you checked against the files as verified.
3. **Gaps**: what Neon could not see (`refused`, `outside_workspace`, files you left unstaged) and how that limits the answer.
4. **Follow-up handle**: the run path and `session_id`, so a later brief can continue the same consultation.
5. **Local copies**: the staged files remain under the run path, and agy keeps the session under `~/.gemini/antigravity-cli/brain/<session_id>` and `~/.gemini/antigravity-cli/conversations/<session_id>.db`. Say whether either holds anything sensitive.
