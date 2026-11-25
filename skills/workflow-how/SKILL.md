---
name: workflow-how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation."
disable-model-invocation: true
---

This collection uses category-prefixed invocation names. When referring to another bundled skill, use its name from [the collection map](COLLECTION.md).

# How

Explore the codebase to answer "how does X work?" questions.

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

## 1. Explain

Use the host agent's subagent tool to spawn one delegate that explores and explains in one pass. Give it a read-only scope: inspect the codebase and report findings without editing files or changing external state. Use a read-only tool option when the host provides one. Choose available models and reasoning settings suited to the task, honoring the user's configured preferences. If a requested model or setting is unavailable, inherit the parent agent's supported configuration and disclose the fallback. If the host has no subagent tool, perform the same exploration and explanation directly and say that no delegate was used.

Give the delegate, or use directly, the user's question and this brief:

> You are writing an architectural explanation for a senior engineer. Explore the codebase and write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model. They should understand the architecture well enough to start working in it confidently. You have read-only access to the codebase.

## 2. Present

Present the subagent's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.
