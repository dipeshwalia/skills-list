<p align="center">
  <img src="assets/brand/banner.svg" alt="Skills List — Engineering skills, made personal. Curated by Dipesh Walia." width="1280" />
</p>

<p align="center">
  <a href="INVENTORY.md">Inventory & credits</a> ·
  <a href="docs/skillshare.md">Skillshare setup</a> ·
  <a href="docs/upstreams.md">Upstream workflow</a>
</p>

**A personal collection of AI agent skills for planning, building, and reviewing software.** Curated by [Dipesh Walia](https://github.com/dipeshwalia), with editable upstream copies, traceable updates, and credit to every original source.

Keep the skills that fit your work. Adapt them in place. Bring in improvements from their original repositories with Git subtrees, then use [Skillshare](https://github.com/runkids/skillshare) to make your selected copies available to your AI tools.

## In the collection

The starting collection features four workflows by **[Matt Pocock](https://github.com/mattpocock/skills)**:

| Skill | What it helps you do | Original source |
| --- | --- | --- |
| [grill-with-docs](upstreams/mattpocock/skills/engineering/grill-with-docs/SKILL.md) | Sharpen a design through questions while building its documentation. | [Matt Pocock](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs) |
| [wayfinder](upstreams/mattpocock/skills/engineering/wayfinder/SKILL.md) | Map a large effort into decisions and work through the unknowns. | [Matt Pocock](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder) |
| [to-tickets](upstreams/mattpocock/skills/engineering/to-tickets/SKILL.md) | Turn a plan into implementation tickets with clear dependencies. | [Matt Pocock](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets) |
| [implement-spec](upstreams/mattpocock/skills/engineering/implement-spec/SKILL.md) | Coordinate implementation of a specification and its ticket graph. | [Matt Pocock](https://github.com/mattpocock/skills/tree/main/skills/engineering/implement-spec) |

Eight supporting skills complete these workflows. The [full inventory](INVENTORY.md) records their roles, original authors, licenses, and exact upstream revisions. The original instructions and invocation settings are preserved.

## Get started

Requires Python 3 and Git with `git subtree`. Clone with Git so the upstream merge history comes with the files:

```sh
git clone https://github.com/dipeshwalia/skills-list.git
cd skills-list
python3 scripts/upstream.py list
```

To use the skills in an agent, follow the [Skillshare setup guide](docs/skillshare.md). Adapt [the configuration example](skillshare.config.example.yaml) so `sources.skills` points to **your checkout's root**, covering both `skills/` and `upstreams/`.

The root [`.skillignore`](.skillignore) selects the four workflows and their eight supporting skills. Other imported skills remain available to review and select later. Preview your configured targets with `skillshare sync -g --dry-run` before syncing.

## Keep your copies current

Commit your local work, then preview and merge updates from the configured parent repositories:

```sh
./scripts/sync-upstreams.sh --dry-run
./scripts/sync-upstreams.sh
```

Pass a source name, such as `mattpocock`, to update it individually. Sync preserves local customizations through normal Git merges and stops on conflicts. Review changed instructions, dependencies, and source credits before using an update.

See [the upstream workflow](docs/upstreams.md) for adding sources, customizing skills, resolving conflicts, and preserving attribution. `origin` is this repository; original parent sources live in [`upstreams.json`](upstreams.json).

## Repository map

```text
skills/                         Your original skills
upstreams/<source>/             Editable copies of original repositories
INVENTORY.md                    Selected skills and original-source credits
upstreams.json                  Parent repository URLs and refs
.skillignore                    Skills selected for Skillshare
skillshare.config.example.yaml  Agent distribution settings
scripts/sync-upstreams.sh       Update imported parents
docs/                          Setup and maintenance guides
assets/brand/                   Repository identity and preview artwork
```

Run the sync helper's checks with `python3 -m unittest discover -s tests -v`. They use temporary local Git repositories and require no network access.

## Credit stays with the work

This collection's curation and maintenance are by [Dipesh Walia](https://github.com/dipeshwalia). Imported skills retain their original authorship and applicable licenses. The initial collection is from [Matt Pocock](https://github.com/mattpocock/skills), under his repository's [MIT license](upstreams/mattpocock/LICENSE).

Each selected imported skill includes `UPSTREAM.md` and `LICENSE.upstream`, so source links, revision details, and license notices travel with individual copies. Existing inline acknowledgements and upstream notices remain intact. See [the inventory and attribution policy](INVENTORY.md) for every source.
