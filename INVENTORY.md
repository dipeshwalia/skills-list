# Skill inventory and original-source credits

This repository curates locally maintained copies. Original authors retain credit for their work. The four requested skills below and their eight supporting dependencies are selected in [`.skillignore`](.skillignore), ready for Skillshare to distribute after configuration. Selection here does not install them into an agent.

## Original source

| Source | Original author | License | Reviewed upstream revision |
| --- | --- | --- | --- |
| [mattpocock/skills](https://github.com/mattpocock/skills) | [Matt Pocock](https://github.com/mattpocock) | [MIT — Copyright (c) 2026 Matt Pocock](upstreams/mattpocock/LICENSE) | [`4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`](https://github.com/mattpocock/skills/commit/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d) |

The whole source repository is retained as a Git subtree for mergeable upstream updates. Only the directories listed below are selected for Skillshare. The original instructions, supporting resources, inline credits, and invocation metadata are unchanged. Local additions are `UPSTREAM.md` and `LICENSE.upstream` in each selected skill directory.

## Requested skills

| Skill | Purpose | Original author and source | Local copy |
| --- | --- | --- | --- |
| `grill-with-docs` | Interview a design while developing its domain documentation. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/grill-with-docs) | [SKILL.md](upstreams/mattpocock/skills/engineering/grill-with-docs/SKILL.md) |
| `wayfinder` | Plan a large effort through linked decision tickets. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/wayfinder) | [SKILL.md](upstreams/mattpocock/skills/engineering/wayfinder/SKILL.md) |
| `to-tickets` | Break a plan into implementation tickets with blocking relationships. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/to-tickets) | [SKILL.md](upstreams/mattpocock/skills/engineering/to-tickets/SKILL.md) |
| `implement-spec` | Coordinate implementation of a specification and its ticket graph. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/implement-spec) | [SKILL.md](upstreams/mattpocock/skills/engineering/implement-spec/SKILL.md) |

## Supporting dependencies

These complete the selected workflows, including their conditional branches. They are not additional primary inventory requests.

| Skill | Why it is included | Original author and source | Local copy |
| --- | --- | --- | --- |
| `grilling` | Called by `grill-with-docs` and `wayfinder`. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grilling) | [SKILL.md](upstreams/mattpocock/skills/productivity/grilling/SKILL.md) |
| `domain-modeling` | Called alongside `grilling` by both workflows. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/domain-modeling) | [SKILL.md](upstreams/mattpocock/skills/engineering/domain-modeling/SKILL.md) |
| `tdd` | Used by `implement-spec` implementer agents. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd) | [SKILL.md](upstreams/mattpocock/skills/engineering/tdd/SKILL.md) |
| `code-review` | Final implementation review; also referenced by `tdd`. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/code-review) | [SKILL.md](upstreams/mattpocock/skills/engineering/code-review/SKILL.md) |
| `research` | Conditional: Wayfinder research tickets. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/research) | [SKILL.md](upstreams/mattpocock/skills/engineering/research/SKILL.md) |
| `prototype` | Conditional: Wayfinder prototype tickets. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/prototype) | [SKILL.md](upstreams/mattpocock/skills/engineering/prototype/SKILL.md) |
| `codebase-design` | Conditional: interface and test-seam design questions during `tdd`. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/codebase-design) | [SKILL.md](upstreams/mattpocock/skills/engineering/codebase-design/SKILL.md) |
| `setup-matt-pocock-skills` | Per-project tracker and documentation setup when not already configured. Included but not run during inventory setup. | [Matt Pocock · original](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/setup-matt-pocock-skills) | [SKILL.md](upstreams/mattpocock/skills/engineering/setup-matt-pocock-skills/SKILL.md) |

## Keep attribution with each copy

Every selected skill contains:

- `UPSTREAM.md`: original author, original directory, immutable upstream revision, and local-change status.
- `LICENSE.upstream`: the upstream license text verbatim, including its copyright and permission notices.

Keep both files when copying, adapting, exporting, or sharing a skill. Preserve any additional upstream `CREDITS`, `NOTICE`, license files, and inline acknowledgements. For example, the imported design and review guidance retains its references to Michael Feathers, John Ousterhout, and Martin Fowler.

For each new original source, add its author, repository, applicable license, and reviewed commit here before selecting its skills. After an upstream merge, review changed authorship and licensing, refresh these provenance records and dependency selections, and distinguish local edits from the original work. Do not describe locally customized instructions as unchanged.
