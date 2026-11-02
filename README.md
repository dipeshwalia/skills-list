<p align="center">
  <img src="assets/brand/banner.svg" alt="Skills List — Engineering skills, made personal. Curated by Dipesh Walia." width="1280" />
</p>

<p align="center">
  <a href="skills/README.md">Browse skills</a> ·
  <a href="INVENTORY.md">Inventory & credits</a> ·
  <a href="docs/skillshare.md">Skillshare setup</a> ·
  <a href="docs/upstreams.md">Upstream workflow</a>
</p>

**A personal collection of AI agent skills for planning, building, reviewing, and writing.** Curated by [Dipesh Walia](https://github.com/dipeshwalia), with editable upstream copies, mergeable updates, and credit to every original source.

## Invoke by category

Category names become invocation prefixes. The skill's original name identifies its domain within the category:

| Category | Examples | Browse |
| --- | --- | --- |
| Workflow | `/workflow-improve`, `/workflow-grill-me`, `/workflow-tdd`, `/workflow-dry-refactoring` | [Workflow skills](skills/README.md#workflow) |
| Writing | `/writing-unslop`, `/writing-technical-writing`, `/writing-i-have-adhd`, `/writing-simple-english` | [Writing skills](skills/README.md#writing) |

The [skills directory](skills/) contains real packages named `workflow-improve`, `writing-unslop`, and so on. Hosts may expose their own invocation syntax; these are the installed skill names. The [full inventory](INVENTORY.md) records every selected skill, supporting dependency, original author, license, and reviewed revision.

## Get started

Requires Python 3 and Git with `git subtree`. Clone with Git so the upstream merge history travels with the files:

```sh
git clone https://github.com/dipeshwalia/skills-list.git
cd skills-list
python3 scripts/build-skills.py --check
```

To distribute the packages, follow the [Skillshare setup guide](docs/skillshare.md). Adapt [the configuration example](skillshare.config.example.yaml) so `sources.skills` points at your checkout's root. The root [`.skillignore`](.skillignore) selects only `skills/`, and `target_naming: standard` preserves the category-prefixed names.

## Select and customize

Edit [sources.json](sources.json) to choose a source, category, and optional list of skill names. [sources.ts](sources.ts) exports the same data through the `Source` interface. Omitting `skills` selects every canonical skill in that source.

Edit the canonical copies under `upstreams/`, then generate the packages:

```sh
python3 scripts/build-skills.py
python3 scripts/build-skills.py --check
```

The builder keeps references, scripts, invocation metadata, credits, and licenses. It updates package names and selected sibling links. It refuses to overwrite manual edits in generated packages; make customizations in the canonical source instead.

## Keep your copies current

Commit local work, then preview and merge updates from the configured parent repositories:

```sh
./scripts/sync-upstreams.sh --dry-run
./scripts/sync-upstreams.sh
```

Pass source names to update individual parents. Successful syncs rebuild the category packages for review. Inspect the changes, refresh reviewed attribution where needed, rebuild again, and commit the results before running `skillshare sync -g`.

See [the upstream workflow](docs/upstreams.md) for adding sources and resolving conflicts. `origin` is this repository; original parent sources live in [upstreams.json](upstreams.json).

## Repository map

```text
sources.json                    Source selections and invocation categories
sources.ts                      Typed Source interface and manifest export
skills/<category>-<name>/       Generated installable packages
skills/README.md                Categorized catalog
upstreams/<source>/             Editable canonical copies and merge history
upstreams.json                  Parent repository URLs and refs
INVENTORY.md                    Original-source credits and reviewed revisions
scripts/build-skills.py         Build or check category packages
scripts/sync-upstreams.sh       Merge original parent updates
skillshare.config.example.yaml Agent distribution settings
docs/                          Setup and maintenance guides
assets/brand/                  Repository identity and preview artwork
```

Run `python3 -m unittest discover -s tests -v` for the local fixture checks.

## Credit stays with the work

Curation and maintenance are by Dipesh Walia. Imported work retains its original authorship: Matt Pocock, Lauren Tan, Ayoub Ghriss, AminBlg, Andrey Kucherenko, and shadcn. Each selected package carries its original license and provenance. See [the inventory](INVENTORY.md) for source links, license notices, and the precise local adaptations.
