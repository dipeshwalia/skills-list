# Skillshare integration

Git subtrees maintain editable copies of the original repositories. The package builder gives selected skills category-prefixed names. Skillshare distributes those generated packages to your AI tools.

## Configure the source

Use your checkout's root as `sources.skills`. The root `.skillignore` includes only skill directories under `skills/`; canonical copies under `upstreams/` are excluded so the same skill is not exposed twice.

```text
skills-list/                         # sources.skills
├── .skillignore
├── sources.json                     # Source selections and categories
├── skills/
│   ├── workflow-improve/SKILL.md
│   ├── writing-unslop/SKILL.md
│   └── ...
└── upstreams/                       # Editable canonical copies
```

Merge [the configuration example](../skillshare.config.example.yaml) into `~/.config/skillshare/config.yaml`, adjusting paths for your machine:

```yaml
sources:
  skills: ~/skills-list
mode: merge
target_naming: standard
targets:
  codex:
    skills:
      path: ~/.codex/skills
```

`mode: merge` creates a link for each enabled skill and preserves unrelated target skills. It does not perform Git merges. `target_naming: standard` uses the package's `name`, such as `workflow-improve`; it avoids flattened names such as `skills__workflow-improve`.

The example is not loaded automatically. Adding packages here does not change global configuration, install a CLI, or update your agent directories.

## Select skills and categories

Edit [sources.json](../sources.json). Each entry contains `source`, `category`, and optionally `skills`:

```json
{
  "source": "mattpocock/skills",
  "category": "Workflow",
  "skills": ["grill-me", "tdd"]
}
```

The category becomes a lowercase invocation prefix: `Workflow` plus `tdd` produces `workflow-tdd`. The original name is the domain within the category. The [TypeScript interface](../sources.ts) exposes the same manifest to code consumers.

A source can name a whole repository or a skill subdirectory. With no `skills` list, the builder includes every canonical skill under that source. Review additions and their dependencies before broadening a selection.

Generate and check the packages after changing the manifest or a canonical skill:

```sh
python3 scripts/build-skills.py
python3 scripts/build-skills.py --check
```

The builder requires source attribution and license files. It retains resources and invocation metadata, prefixes names, and updates selected sibling links. Each package includes `COLLECTION.md` so references to original skill names can be resolved to the collection's invocation names.

Edit imported instructions under `upstreams/`. Generated packages are checked against their saved hashes before replacement. If you edited a generated package, move the change to its canonical source, preserve any work you need, restore the generated copy from Git, then rebuild.

## Preview and sync

After installing Skillshare and configuring its global source and targets:

```sh
skillshare list -g
skillshare sync -g --dry-run
skillshare sync -g
```

Use `-g` explicitly when another project has its own `.skillshare/` configuration. Review the dry run for name collisions before syncing. Hosts may expose slash commands or another invocation syntax; the selected package names are prefixed in either case.

Existing links reflect source-file edits immediately. Run sync to add or remove links after the package set changes. A target using `copy` mode needs another sync after package content changes.

When migrating from the old unprefixed names, existing target links can remain after sync. After previewing and syncing the prefixed packages, remove only obsolete target symlinks that resolve inside this checkout's `upstreams/` directory. Leave canonical source files and unrelated target files untouched.

For per-tool selection, use target `include`/`exclude` filters. These match flattened discovery names such as `skills__workflow-improve`, even with `target_naming: standard`. Machine-only exclusions can also go in `.skillignore.local`, which is Git-ignored.

## Upstream updates

```sh
./scripts/sync-upstreams.sh --dry-run
./scripts/sync-upstreams.sh
python3 scripts/build-skills.py --check
skillshare sync -g --dry-run
```

Review upstream changes and refresh provenance before distributing them. The subtree helper rebuilds packages after successful merges, but it does not run Skillshare. Its Git merge workflow is separate from Skillshare's `update` command and `install --track` clones.

See [the upstream workflow](upstreams.md) for customization and conflict resolution, and [the inventory](../INVENTORY.md) for credits and usage-time prerequisites.

## References

- [Skillshare configuration schema](https://github.com/runkids/skillshare/blob/51d299ff07ba4eeaff1b8929aa803c826d0a9ae1/schemas/config.schema.json)
- [Organizing skills](https://skillshare.runkids.cc/docs/how-to/daily-tasks/organizing-skills/)
- [Sync modes and naming](https://skillshare.runkids.cc/docs/understand/sync-modes/)
- [Filtering](https://skillshare.runkids.cc/docs/reference/filtering/)
