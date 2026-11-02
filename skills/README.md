# Skills

Use the category prefix when invoking a skill: `/workflow-improve`, `/workflow-tdd`, or `/writing-unslop`. The original skill name is its domain within that category. Your host may use different invocation syntax, but the installed names include these prefixes.

These folders contain the actual installable packages. [sources.json](../sources.json) selects the sources, categories, and skill names; [sources.ts](../sources.ts) exposes the same manifest through the `Source` interface.

## Workflow

| Invocation | Original skill | Purpose | Original source |
| --- | --- | --- | --- |
| [`/workflow-grill-with-docs`](workflow-grill-with-docs/SKILL.md) | `grill-with-docs` | Interview a design while building its domain documentation. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/grill-with-docs) |
| [`/workflow-wayfinder`](workflow-wayfinder/SKILL.md) | `wayfinder` | Plan a large effort through linked decision tickets. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/wayfinder) |
| [`/workflow-to-tickets`](workflow-to-tickets/SKILL.md) | `to-tickets` | Break a plan into implementation tickets and dependencies. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/to-tickets) |
| [`/workflow-implement-spec`](workflow-implement-spec/SKILL.md) | `implement-spec` | Coordinate implementation of a specification and its tickets. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/implement-spec) |
| [`/workflow-grill-me`](workflow-grill-me/SKILL.md) | `grill-me` | Sharpen a plan or design through questions. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grill-me) |
| [`/workflow-grilling`](workflow-grilling/SKILL.md) | `grilling` | Work through decisions with focused questions. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grilling) |
| [`/workflow-handoff`](workflow-handoff/SKILL.md) | `handoff` | Prepare context for another agent or session. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/handoff) |
| [`/workflow-to-questionnaire`](workflow-to-questionnaire/SKILL.md) | `to-questionnaire` | Turn open questions into an answerable questionnaire. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/to-questionnaire) |
| [`/workflow-writing-for-agents`](workflow-writing-for-agents/SKILL.md) | `writing-for-agents` | Write instructions and context for agent readers. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/writing-for-agents) |
| [`/workflow-teach`](workflow-teach/SKILL.md) | `teach` | Build a learning plan and track understanding. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/teach) |
| [`/workflow-code-review`](workflow-code-review/SKILL.md) | `code-review` | Review an implementation for correctness and design. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/code-review) |
| [`/workflow-codebase-design`](workflow-codebase-design/SKILL.md) | `codebase-design` | Design interfaces, boundaries, and test seams. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/codebase-design) |
| [`/workflow-research`](workflow-research/SKILL.md) | `research` | Investigate an unfamiliar topic or technical question. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/research) |
| [`/workflow-tdd`](workflow-tdd/SKILL.md) | `tdd` | Develop through tests and incremental implementation. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd) |
| [`/workflow-domain-modeling`](workflow-domain-modeling/SKILL.md) | `domain-modeling` | Support the design interviews in grill-with-docs and wayfinder. Supporting dependency. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/domain-modeling) |
| [`/workflow-to-spec`](workflow-to-spec/SKILL.md) | `to-spec` | Write specifications consumed by implementation and ticket workflows. Supporting dependency. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/to-spec) |
| [`/workflow-prototype`](workflow-prototype/SKILL.md) | `prototype` | Resolve uncertain design questions with a prototype. Supporting dependency. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/prototype) |
| [`/workflow-setup-matt-pocock-skills`](workflow-setup-matt-pocock-skills/SKILL.md) | `setup-matt-pocock-skills` | Configure a project’s tracker and documentation conventions. Supporting dependency. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/setup-matt-pocock-skills) |
| [`/workflow-how`](workflow-how/SKILL.md) | `how` | Explain architecture, runtime flow, and ownership boundaries. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/how) |
| [`/workflow-statechart`](workflow-statechart/SKILL.md) | `statechart` | Check TLA+ state models and produce Mermaid statecharts. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/statechart) |
| [`/workflow-dry-refactoring`](workflow-dry-refactoring/SKILL.md) | `dry-refactoring` | Refactor confirmed duplication detected by jscpd. | [Andrey Kucherenko · original](https://github.com/kucherenko/jscpd/tree/0b519608c47d287f59018ce4ad7f9939ac93e0c8/skills/dry-refactoring) |
| [`/workflow-jscpd`](workflow-jscpd/SKILL.md) | `jscpd` | Detect duplication before dry-refactoring. Supporting dependency. | [Andrey Kucherenko · original](https://github.com/kucherenko/jscpd/tree/0b519608c47d287f59018ce4ad7f9939ac93e0c8/skills/jscpd) |
| [`/workflow-improve`](workflow-improve/SKILL.md) | `improve` | Audit a codebase and prepare plans for another agent to execute. | [shadcn · original](https://github.com/shadcn/improve/tree/cac56e1ebd3c279aa9153616cfeac7b174ab90f9/skills/improve) |

## Writing

| Invocation | Original skill | Purpose | Original source |
| --- | --- | --- | --- |
| [`/writing-technical-writing`](writing-technical-writing/SKILL.md) | `technical-writing` | Write and review structured technical documentation. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/technical-writing) |
| [`/writing-unslop`](writing-unslop/SKILL.md) | `unslop` | Remove filler and common AI writing patterns. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/unslop) |
| [`/writing-i-have-adhd`](writing-i-have-adhd/SKILL.md) | `i-have-adhd` | Make answers direct, scannable, and easier to follow. | [Ayoub Ghriss · original](https://github.com/ayghri/i-have-adhd/tree/1ecea1993b7fce257ffbd686c070948b5e07eda6/skills/i-have-adhd) |
| [`/writing-simple-english`](writing-simple-english/SKILL.md) | `simple-english` | Write clear instructions using simplified technical English. | [AminBlg · original](https://github.com/AminBlg/SimpleEnglish/tree/a6fcb4fde098b33617cc1578d151ebf58774b883/skills/simple-english) |

## Maintain the packages

Edit the canonical skill under `upstreams/<source>/`, then run `python3 scripts/build-skills.py`. The builder preserves supporting resources and original-source notices, updates invocation names and selected sibling links, and includes a `COLLECTION.md` alias guide in each package. It refuses to overwrite manual changes in generated packages.

Run `python3 scripts/build-skills.py --check` to verify that the packages match the manifest and source copies. See [the inventory](../INVENTORY.md) for licenses and revisions, [the update workflow](../docs/upstreams.md) for customization, and [Skillshare setup](../docs/skillshare.md) for installation.
