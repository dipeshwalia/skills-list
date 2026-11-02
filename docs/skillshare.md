# Skillshare integration

This repository is the editable source of truth. Git subtrees merge changes from multiple upstream authors; Skillshare discovers the selected skills and links them into your AI tools.

The layout works without moving files into `.skillshare/skills/`. That location is the default for Skillshare's project mode; this personal collection uses global mode with a custom source path.

## Source and configuration

Use the repository root, `/Users/dipeshwalia/personal/skills`, as `sources.skills`. Pointing at its `skills/` child would omit every imported repository under `upstreams/`.

```text
personal/skills/                          # sources.skills
├── .skillignore                          # Shared selection rules
├── .skillignore.local                    # Optional machine-only overrides
├── skillshare.config.example.yaml        # Example, not auto-loaded
├── skills/
│   └── my-workflow/
│       ├── SKILL.md
│       ├── references/                   # Optional
│       ├── scripts/                      # Optional
│       └── assets/                       # Optional
└── upstreams/
    ├── mattpocock/
    │   ├── LICENSE
    │   └── skills/engineering/tdd/SKILL.md
    └── another-author/...
```

Skillshare recursively discovers folders containing `SKILL.md`; intermediate folders need no skill file. There is one skills-source root, which can contain as many upstream directories as needed. Git subtrees contain ordinary files, so no symlink-following setting is needed for discovery.

Skillshare's global config normally lives at `~/.config/skillshare/config.yaml`. Use [the example](../skillshare.config.example.yaml) there, adjusting the source and targets for your machine. Merge settings into any existing config. The example selects Codex; add other targets only when you want to use them.

The relevant settings are:

```yaml
sources:
  skills: ~/personal/skills
mode: merge
target_naming: standard
targets:
  codex:
    skills:
      path: ~/.codex/skills
```

`sources.skills` is the current schema field; legacy `source` is also accepted. `mode: merge` links each skill separately and preserves unrelated skills in the target. It does not perform Git merges. Changes to an already-linked skill are visible immediately; run `sync` to add or remove links. Use `copy` mode for a target that requires real files, and sync again after editing those files at the source.

The whole-directory `symlink` mode is unsuitable for this mixed repository root. Keep the example's per-skill `merge` mode.

## Skill format

Each skill needs a `SKILL.md` with YAML frontmatter and Markdown instructions:

```markdown
---
name: my-workflow
description: Review a proposed implementation against my project's conventions.
---

# My workflow

Describe the specific decisions and actions this skill should guide.
```

For the selected `standard` naming mode:

- Match `name` to the immediate containing folder, such as `my-workflow/`.
- Use at most 64 lowercase letters, digits, and single hyphens; no leading, trailing, or consecutive hyphens.
- Include a useful `description` and nonempty instructions. The prose format guide calls description optional, but Skillshare's current lint rules flag its absence as an error.
- Keep supporting files with the skill and use working relative links. Preserve any agent-specific metadata, including `agents/openai.yaml` when present.
- Give enabled skills unique names. Two authors can both provide `tdd`, but select one version for each target or deliberately rename your customized skill and its folder. Renaming inside a subtree also requires care during future upstream merges.

With `target_naming: standard`, the example upstream skill becomes `tdd` in the target. Default `flat` naming would make it `upstreams__mattpocock__skills__engineering__tdd`. Skillshare warns about invalid names and collisions and skips affected skills.

## Select skills

The root [`.skillignore`](../.skillignore) starts with:

```gitignore
*
!/skills/**
```

These first rules enable your originals. The file also contains exact selections for the four requested Matt Pocock skills and their eight supporting dependencies, documented with original-source credits in [the inventory](../INVENTORY.md). Other imported skills remain unselected. After importing and reviewing more skills, append exact directory selections, for example:

```gitignore
!/upstreams/mattpocock/skills/engineering/tdd
!/upstreams/mattpocock/skills/engineering/codebase-design
!/upstreams/mattpocock/skills/engineering/code-review
```

Check the imported instructions for their current sibling-skill dependencies. To select a collection, use `!/upstreams/mattpocock/skills/engineering/**` after reviewing what that includes.

These patterns match **skill-directory paths relative to the source root**, not `SKILL.md` filenames or individual resource files. Exact selections avoid accidentally enabling test and example skills shipped elsewhere in an upstream repository.

Skillshare does not automatically apply nested `.skillignore` files inside these ordinary Git subtrees. Maintain selections in this root file. Machine-specific overrides can go in `.skillignore.local`, which is Git-ignored and evaluated after the shared rules.

For different selections per tool, use target `include`/`exclude` filters. These match flattened names such as `upstreams__mattpocock__skills__engineering__tdd` even when `target_naming: standard` is enabled. They further restrict the skills allowed by `.skillignore`.

## Preview and use

After installing Skillshare and configuring its global config:

```sh
skillshare version
skillshare list -g
skillshare sync -g --dry-run
skillshare sync -g
```

Use `-g` explicitly to select global mode even when running from another project that has its own `.skillshare/` configuration. Review the dry run for collisions with existing installed skills before syncing.

To update one customized upstream, follow the repository's Git review workflow, then refresh Skillshare's target links:

```sh
python3 scripts/upstream.py sync mattpocock
skillshare sync -g --dry-run
skillshare sync -g
```

Use `./scripts/sync-upstreams.sh` to update all imported parents, or add `--dry-run` to preview. Review the resulting changes and refresh source credits and license copies before distributing the update. The script preserves the existing skill selection and does not run Skillshare itself.

Skillshare does not read `upstreams.json`. Its `install --track` mechanism creates separate Git clones, while regular installs copy skill files and updates reinstall them. The subtree helper remains responsible for merging this repository's upstreams. Avoid registering those same upstreams a second time through Skillshare.

Skillshare configuration examples and selection rules do not install the CLI, configure your global targets, or publish this repository. Imported source content and enabled skill selections are recorded separately in [the inventory](../INVENTORY.md).

## Checked against

Validated with the official Skillshare v0.28.0 CLI in temporary source, config, and target directories. Checks covered nested discovery, the default exclusions, selecting one upstream skill with its resources, standard target names, preserving unrelated target skills, and resolving duplicate-name selection with target filters. No real agent directories were changed.

- [Skillshare configuration schema](https://github.com/runkids/skillshare/blob/51d299ff07ba4eeaff1b8929aa803c826d0a9ae1/schemas/config.schema.json)
- [Organizing skills](https://skillshare.runkids.cc/docs/how-to/daily-tasks/organizing-skills/)
- [Sync modes and naming](https://skillshare.runkids.cc/docs/understand/sync-modes/)
- [Filtering](https://skillshare.runkids.cc/docs/reference/filtering/)
- [Skill format lint rules](https://github.com/runkids/skillshare/blob/51d299ff07ba4eeaff1b8929aa803c826d0a9ae1/internal/sync/lint_rules.yaml)
- [Update behavior](https://skillshare.runkids.cc/docs/reference/commands/update/)
