# Original-source attribution

- Original author: Lauren Tan, as credited in [pstack's plugin metadata](https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/plugin.json).
- Original repository: [cursor/plugins](https://github.com/cursor/plugins), pstack plugin.
- Original skill: [unslop](https://github.com/cursor/plugins/tree/main/pstack/skills/unslop).
- Reviewed upstream revision: [`2776ddd2355d6d6c8747d3964600f28daf62f049`](https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/skills/unslop).
- Original copyright: Copyright (c) 2026 Lauren Tan.
- License: MIT, from [pstack/LICENSE](../../LICENSE); the complete original notice is copied verbatim in [LICENSE.upstream](LICENSE.upstream).

This is a locally maintained copy in Dipesh Walia's personal skills inventory. The original skill instructions and supporting resources are unchanged. One local change: the upstream `disable-model-invocation: true` line is removed from the `SKILL.md` frontmatter. `technical-writing` tells the agent to apply this skill to every document, and hosts that honor that setting, such as Claude Code, stop the agent from loading a skill marked with it. Without the line, the agent can load this skill when `technical-writing` asks for it, and users can still invoke it directly.

Local additions are this provenance file and `LICENSE.upstream`. Keep both with individual copies, and preserve all other upstream notices. After an upstream merge, review changes before updating the reviewed revision or local-change statement.
