---
name: workflow-ask-neon
description: Ask Gemini Neon (xhigh reasoning, through the Antigravity CLI) for a second opinion, review, or analysis when the user says "ask neon" or wants Neon's view.
---

# Ask Neon

A Neon consultation takes 5 to 15 minutes, so a background subagent runs it while you and the user carry on. Your part is the brief going in and the answer coming out.

## 1. Write the brief

The subagent sees none of this conversation: the brief is everything it knows. Write it from the conversation and the user's request:

- **Question**: what Neon should answer, and the output wanted (ranked findings, a recommendation, a review).
- **Facts**: what is already established, so Neon builds on it instead of rediscovering it.
- **Files**: the repository root, as an absolute path, and the files Neon should read, relative to it. Name files, never directories. Leave out customer, subscriber and network data (captures, baselines, evidence files, logs), credentials, and anything the user's data rules keep in-house: whatever Neon reads goes to Google. For a review, give the diff range as well.
- **Constraints**: the user's limits, including whether customers, carriers or tickets may be named or must stay generic.
- **Follow-up**: for a follow-up to an earlier consultation, the run path and `session_id` from that report.

Done when someone with only the brief and the named files could do the consultation.

## 2. Hand it to a background subagent

Start a general-purpose subagent in the background with the Agent tool. Give it this prompt, filling in the two parts:

> Follow `<this skill's directory>/CONSULT.md` exactly, to ask Gemini Neon the question in this brief. Report as its step 5 says.
>
> Brief:
> <the brief>

Then tell the user, in one line, that Neon is consulting and roughly how long it takes, and carry on with anything else they asked. When the host has no subagent tool, follow `CONSULT.md` yourself with the brief.

## 3. Relay the answer

When the subagent reports, give the user Neon's answer: the status, its conclusions attributed to Neon, the gaps, and the follow-up handle. Separate what Neon recommends from what you or the subagent verified, and keep disagreements and uncertainty that affect the user's decision. Apply changes only within the user's authorized task.

When the report says data may have left the workspace, or that agy's local copy holds something sensitive, say so plainly.
