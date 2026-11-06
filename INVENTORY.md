# Skills List — inventory and original-source credits

This collection curates editable upstream copies and publishes category-prefixed skill packages. Original authors retain credit. [sources.json](sources.json) is the single record of selection, authorship, licenses, reviewed revisions, supporting status, and companion skills. `scripts/build-skills.py` validates those records and generates every table on this page; edit the records, not the tables. Selection and generation do not install skills into an agent.

## Original sources

<!-- inventory:sources -->

| Source | Original author | License and copyright | Reviewed upstream revision |
| --- | --- | --- | --- |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Matt Pocock | [MIT — 2026 Matt Pocock](upstreams/mattpocock/LICENSE) | [`4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`](https://github.com/mattpocock/skills/commit/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d) |
| [pstack in cursor/plugins](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack) | Lauren Tan | [MIT — 2026 Lauren Tan](upstreams/cursor-plugins/pstack/LICENSE) | [`ae5650febf4320793844c12c4adaa937f417f8da`](https://github.com/cursor/plugins/commit/ae5650febf4320793844c12c4adaa937f417f8da) |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | Ayoub Ghriss | [MIT — 2026 Ayoub Ghriss](upstreams/i-have-adhd/LICENSE) | [`1ecea1993b7fce257ffbd686c070948b5e07eda6`](https://github.com/ayghri/i-have-adhd/commit/1ecea1993b7fce257ffbd686c070948b5e07eda6) |
| [kucherenko/jscpd](https://github.com/kucherenko/jscpd) | Andrey Kucherenko | [MIT — 2013-2024 Andrey Kucherenko](upstreams/jscpd/LICENSE) | [`0b519608c47d287f59018ce4ad7f9939ac93e0c8`](https://github.com/kucherenko/jscpd/commit/0b519608c47d287f59018ce4ad7f9939ac93e0c8) |
| [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) | AminBlg | [MIT — 2026 AminBlg](upstreams/simple-english/LICENSE) | [`a6fcb4fde098b33617cc1578d151ebf58774b883`](https://github.com/AminBlg/SimpleEnglish/commit/a6fcb4fde098b33617cc1578d151ebf58774b883) |
| [shadcn/improve](https://github.com/shadcn/improve) | shadcn | [MIT — 2026 shadcn](upstreams/improve/LICENSE.md) | [`cac56e1ebd3c279aa9153616cfeac7b174ab90f9`](https://github.com/shadcn/improve/commit/cac56e1ebd3c279aa9153616cfeac7b174ab90f9) |
| [t3dotgg/tstack](https://github.com/t3dotgg/tstack) | Theo Browne | [MIT — 2026 Theo Browne](upstreams/tstack/LICENSE) | [`1085050f3baed1ac724caa4a8166145fb2ac88af`](https://github.com/t3dotgg/tstack/commit/1085050f3baed1ac724caa4a8166145fb2ac88af) |

<!-- /inventory:sources -->

The source repositories remain Git subtrees so upstream updates can merge with local customizations. The pstack license applies to pstack; other plugins in the Cursor repository retain their own authorship and notices.

## Requested skills

<!-- inventory:requested -->

| Category | Invocation / original skill | Purpose | Original author and source | Package |
| --- | --- | --- | --- | --- |
| Workflow | `/workflow-grill-with-docs` / `grill-with-docs` | Interview a design while building its domain documentation. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/grill-with-docs) | [SKILL.md](skills/workflow-grill-with-docs/SKILL.md) |
| Workflow | `/workflow-wayfinder` / `wayfinder` | Plan a large effort through linked decision tickets. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/wayfinder) | [SKILL.md](skills/workflow-wayfinder/SKILL.md) |
| Workflow | `/workflow-to-tickets` / `to-tickets` | Break a plan into implementation tickets and dependencies. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/to-tickets) | [SKILL.md](skills/workflow-to-tickets/SKILL.md) |
| Workflow | `/workflow-implement-spec` / `implement-spec` | Coordinate implementation of a specification and its tickets. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/implement-spec) | [SKILL.md](skills/workflow-implement-spec/SKILL.md) |
| Workflow | `/workflow-grill-me` / `grill-me` | Sharpen a plan or design through questions. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grill-me) | [SKILL.md](skills/workflow-grill-me/SKILL.md) |
| Workflow | `/workflow-grilling` / `grilling` | Work through decisions with focused questions. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grilling) | [SKILL.md](skills/workflow-grilling/SKILL.md) |
| Workflow | `/workflow-handoff` / `handoff` | Prepare context for another agent or session. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/handoff) | [SKILL.md](skills/workflow-handoff/SKILL.md) |
| Workflow | `/workflow-to-questionnaire` / `to-questionnaire` | Turn open questions into an answerable questionnaire. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/to-questionnaire) | [SKILL.md](skills/workflow-to-questionnaire/SKILL.md) |
| Workflow | `/workflow-writing-for-agents` / `writing-for-agents` | Write instructions and context for agent readers. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/writing-for-agents) | [SKILL.md](skills/workflow-writing-for-agents/SKILL.md) |
| Workflow | `/workflow-teach` / `teach` | Build a learning plan and track understanding. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/teach) | [SKILL.md](skills/workflow-teach/SKILL.md) |
| Workflow | `/workflow-code-review` / `code-review` | Review an implementation for correctness and design. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/code-review) | [SKILL.md](skills/workflow-code-review/SKILL.md) |
| Workflow | `/workflow-codebase-design` / `codebase-design` | Design interfaces, boundaries, and test seams. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/codebase-design) | [SKILL.md](skills/workflow-codebase-design/SKILL.md) |
| Workflow | `/workflow-research` / `research` | Investigate an unfamiliar topic or technical question. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/research) | [SKILL.md](skills/workflow-research/SKILL.md) |
| Workflow | `/workflow-tdd` / `tdd` | Develop through tests and incremental implementation. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd) | [SKILL.md](skills/workflow-tdd/SKILL.md) |
| Workflow | `/workflow-how` / `how` | Explain architecture, runtime flow, and ownership boundaries. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/how) | [SKILL.md](skills/workflow-how/SKILL.md) |
| Workflow | `/workflow-statechart` / `statechart` | Check TLA+ state models and produce Mermaid statecharts. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/statechart) | [SKILL.md](skills/workflow-statechart/SKILL.md) |
| Writing | `/writing-technical-writing` / `technical-writing` | Write and review structured technical documentation. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/technical-writing) | [SKILL.md](skills/writing-technical-writing/SKILL.md) |
| Writing | `/writing-unslop` / `unslop` | Remove filler and common AI writing patterns. | [Lauren Tan · original](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/unslop) | [SKILL.md](skills/writing-unslop/SKILL.md) |
| Writing | `/writing-i-have-adhd` / `i-have-adhd` | Make answers direct, scannable, and easier to follow. | [Ayoub Ghriss · original](https://github.com/ayghri/i-have-adhd/tree/1ecea1993b7fce257ffbd686c070948b5e07eda6/skills/i-have-adhd) | [SKILL.md](skills/writing-i-have-adhd/SKILL.md) |
| Workflow | `/workflow-dry-refactoring` / `dry-refactoring` | Refactor confirmed duplication detected by jscpd. | [Andrey Kucherenko · original](https://github.com/kucherenko/jscpd/tree/0b519608c47d287f59018ce4ad7f9939ac93e0c8/skills/dry-refactoring) | [SKILL.md](skills/workflow-dry-refactoring/SKILL.md) |
| Writing | `/writing-simple-english` / `simple-english` | Write clear instructions using simplified technical English. | [AminBlg · original](https://github.com/AminBlg/SimpleEnglish/tree/a6fcb4fde098b33617cc1578d151ebf58774b883/skills/simple-english) | [SKILL.md](skills/writing-simple-english/SKILL.md) |
| Workflow | `/workflow-improve` / `improve` | Audit a codebase and prepare plans for another agent to execute. | [shadcn · original](https://github.com/shadcn/improve/tree/cac56e1ebd3c279aa9153616cfeac7b174ab90f9/skills/improve) | [SKILL.md](skills/workflow-improve/SKILL.md) |
| T3 | `/t3-full-send` / `full-send` | Complete a change through verification, review, and a merged pull request. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/full-send) | [SKILL.md](skills/t3-full-send/SKILL.md) |
| T3 | `/t3-full-stop` / `full-stop` | Prepare a verified, reviewed pull request for the user to merge. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/full-stop) | [SKILL.md](skills/t3-full-stop/SKILL.md) |
| T3 | `/t3-council` / `council` | Gather and reconcile reviews from three model providers. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/council) | [SKILL.md](skills/t3-council/SKILL.md) |
| T3 | `/t3-sol-loop` / `sol-loop` | Review changes with GPT Sol through bounded feedback rounds. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/sol-loop) | [SKILL.md](skills/t3-sol-loop/SKILL.md) |
| T3 | `/t3-file-pr` / `file-pr` | File a concise pull request that explains the problem and solution. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/file-pr) | [SKILL.md](skills/t3-file-pr/SKILL.md) |
| T3 | `/t3-takeover` / `takeover` | Finish existing work while preserving its contributors’ credit. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/takeover) | [SKILL.md](skills/t3-takeover/SKILL.md) |
| T3 | `/t3-babysit-pr` / `babysit-pr` | Monitor pull request checks and reviews and address verified findings. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/babysit-pr) | [SKILL.md](skills/t3-babysit-pr/SKILL.md) |
| T3 | `/t3-modernize` / `modernize` | Rebase an older pull request and reassess whether its change still belongs. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/modernize) | [SKILL.md](skills/t3-modernize/SKILL.md) |
| T3 | `/t3-leaving-pr-comments` / `leaving-pr-comments` | Write concise GitHub comments with explicit agent attribution. | [Theo Browne · original](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/leaving-pr-comments) | [SKILL.md](skills/t3-leaving-pr-comments/SKILL.md) |

<!-- /inventory:requested -->

## Supporting dependencies

These complete the selected workflows. They are included separately from the user-requested skills, and each one must be required or recommended by another selected skill.

<!-- inventory:supporting -->

| Category | Invocation / original skill | Purpose | Original author and source | Package |
| --- | --- | --- | --- | --- |
| Workflow | `/workflow-domain-modeling` / `domain-modeling` | Support the design interviews in grill-with-docs and wayfinder. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/domain-modeling) | [SKILL.md](skills/workflow-domain-modeling/SKILL.md) |
| Workflow | `/workflow-to-spec` / `to-spec` | Write specifications consumed by implementation and ticket workflows. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/to-spec) | [SKILL.md](skills/workflow-to-spec/SKILL.md) |
| Workflow | `/workflow-prototype` / `prototype` | Resolve uncertain design questions with a prototype. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/prototype) | [SKILL.md](skills/workflow-prototype/SKILL.md) |
| Workflow | `/workflow-setup-matt-pocock-skills` / `setup-matt-pocock-skills` | Configure a project’s tracker and documentation conventions. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/setup-matt-pocock-skills) | [SKILL.md](skills/workflow-setup-matt-pocock-skills/SKILL.md) |
| Workflow | `/workflow-jscpd` / `jscpd` | Detect duplication before dry-refactoring. | [Andrey Kucherenko · original](https://github.com/kucherenko/jscpd/tree/0b519608c47d287f59018ce4ad7f9939ac93e0c8/skills/jscpd) | [SKILL.md](skills/workflow-jscpd/SKILL.md) |

<!-- /inventory:supporting -->

## Companion skills

The builder rejects a selection that leaves out a required companion. Recommendations are optional and may name skills this collection does not include.

<!-- inventory:companions -->

| Skill | Requires (enforced) | Recommends (optional) |
| --- | --- | --- |
| `grill-with-docs` | `grilling`, `domain-modeling` | — |
| `wayfinder` | `grilling`, `domain-modeling`, `research`, `prototype`, `setup-matt-pocock-skills` | — |
| `to-tickets` | `setup-matt-pocock-skills` | — |
| `implement-spec` | `tdd`, `code-review`, `setup-matt-pocock-skills` | `to-spec`, `to-tickets` |
| `grill-me` | `grilling` | — |
| `code-review` | `setup-matt-pocock-skills` | — |
| `tdd` | `codebase-design` | — |
| `to-spec` | `setup-matt-pocock-skills` | — |
| `how` | — | `why` (not selected) |
| `technical-writing` | `unslop` | — |
| `dry-refactoring` | `jscpd` | — |
| `jscpd` | — | `compare-codebases` (not selected), `code-migration` (not selected) |
| `full-send` | `sol-loop`, `file-pr`, `babysit-pr` | — |
| `full-stop` | `full-send` | — |
| `file-pr` | `leaving-pr-comments` | `babysit-pr` |
| `takeover` | `modernize`, `file-pr`, `babysit-pr`, `leaving-pr-comments` | — |
| `babysit-pr` | `leaving-pr-comments` | — |
| `modernize` | `leaving-pr-comments` | — |

<!-- /inventory:companions -->

## Local changes and runtime requirements

- Generated packages prefix the skill name with its category, rewrite explicit invocations (including quoted names in Skill tool instructions) and selected sibling links, and add a `COLLECTION.md` alias guide. Canonical upstream directories retain their original names. Credits and licenses travel with both copies.
- The canonical pstack `how` copy uses host-supported delegation and model settings, with direct exploration when delegation is unavailable. Its [provenance](upstreams/cursor-plugins/pstack/skills/how/UPSTREAM.md) records that change.
- The canonical `jscpd` copy links its optional comparison workflows to the reviewed upstream revision. Those optional skills are not selected; [its provenance](upstreams/jscpd/skills/jscpd/UPSTREAM.md) records the link change.
- Original invocation settings remain intact except in `unslop`. The pstack `how`, `statechart`, and `technical-writing` skills retain `disable-model-invocation: true`; `i-have-adhd` also retains its explicit-only agent metadata. Hosts that honor those fields require explicit invocation.
- The canonical `unslop` copy drops `disable-model-invocation: true` so the agent can load it when `technical-writing` asks for it; its [provenance](upstreams/cursor-plugins/pstack/skills/unslop/UPSTREAM.md) records that change. Generated sibling links in `dry-refactoring` resolve to `workflow-jscpd`.
- `statechart` includes its scripts and references. Its package leaves out the upstream `scripts/test` fixtures, which only its developers use. Running it needs a supported JavaScript or TypeScript runtime and TLC with Java, with setup through `mise`; image rendering uses Pele.
- `dry-refactoring` and `jscpd` use the jscpd CLI when invoked. `improve` can audit without subagents, but its optional `execute` mode requires isolated-worktree delegation and host-compatible model settings.
- This inventory does not install runtime dependencies or activate upstream plugin hooks. `simple-english` includes its four reference files, not the copyrighted official STE dictionary.
- The `t3-` namespace contains all nine tstack skills by Theo Browne. Its GitHub workflows need an authenticated `gh` CLI; `babysit-pr` includes the original executable `scripts/pr-wait`, which uses Python 3 and POSIX file locking. `council` needs models from three providers, and `sol-loop` needs a host that can delegate to GPT Sol. T3 Code integrations are used when available, with the upstream's documented alternatives elsewhere.

## Keep attribution with each copy

Every selected canonical skill and generated package includes `UPSTREAM.md` and `LICENSE.upstream`. These record the original author, source path, reviewed revision, applicable license, and local changes. Keep both files with copied or shared skills, along with all other upstream notices and inline acknowledgements. The builder checks that each `LICENSE.upstream` matches its project's license file byte for byte.

Updates follow one sequence: merge upstreams, review the changes and provenance, then build. A merge publishes nothing. The builder refuses to publish until a project's `reviewed` revision in sources.json matches the revision merged into its subtree, and until each selected skill's `UPSTREAM.md` names that revision.
