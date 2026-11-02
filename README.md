# Personal LLM skills

Keep your original skills and customized skills from multiple authors in one Git repository. Each upstream has an independent Git subtree, so your edits and upstream changes can be merged using normal Git conflict resolution.

```text
skills/
  my-skill/SKILL.md              # Your original skills
upstreams/                      # Created when you import a source
  mattpocock/                    # Your editable copy of this repository
    skills/engineering/...
  another-author/...
upstreams.json                  # Source repositories and tracked refs
scripts/upstream.py             # Small wrapper around Git subtree
.skillignore                    # Which skills Skillshare can discover
skillshare.config.example.yaml   # Global Skillshare config example
```

Matt Pocock's repository is configured as an example. No external skills are imported or installed by the initial setup.

## Start

Requires Python 3 and Git with `git subtree`. This folder must be its own Git repository with at least one commit before importing a source:

```sh
git init -b main
git add .gitignore .skillignore AGENTS.md README.md upstreams.json scripts skills docs skillshare.config.example.yaml
git commit -m "Set up personal skills repository"
```

Your eventual `origin` remote is your personal repository. Upstream sources are configured separately and do not need to be added as Git remotes.

## Import and customize

```sh
python3 scripts/upstream.py list
python3 scripts/upstream.py sync mattpocock --dry-run
python3 scripts/upstream.py sync mattpocock
```

The first sync imports the **whole upstream repository**, including its license and supporting files, into `upstreams/mattpocock/`. Later syncs merge updates into that directory. Imports and updates with upstream changes create local Git commits; they do not publish them. An already-current source needs no new commit. `--squash` keeps upstream history compact while retaining the baseline needed for subsequent merges.

Edit the imported skill in place, for example:

```text
upstreams/mattpocock/skills/engineering/tdd/SKILL.md
```

Then commit your customization normally. Keep the imported directory at the same path. Original skills go in `skills/<skill-name>/`, with a `SKILL.md` containing `name` and `description` frontmatter.

## Add more upstreams

Add another named entry to `upstreams.json`:

```json
{
  "mattpocock": {
    "repository": "https://github.com/mattpocock/skills.git",
    "ref": "main"
  },
  "another-author": {
    "repository": "https://github.com/OWNER/REPOSITORY.git",
    "ref": "main"
  }
}
```

Replace the example URL and ref with the actual source. Commit the configuration, then run `python3 scripts/upstream.py sync another-author`. Each name maps to `upstreams/<name>/`. Use a source's existing branch, tag, or a commit fetchable from that repository as its ref. Treat source names as permanent after import.

The configuration records where updates come from; subtree commits record the exact upstream revisions already imported. A source stays at its imported version until you explicitly sync it.

## Merge upstream updates

Commit your current work first, including any new files. Use a branch to review an update:

```sh
git switch -c update-mattpocock
python3 scripts/upstream.py sync mattpocock
git diff main...HEAD -- upstreams/mattpocock
```

If both sides edit the same content, Git leaves a normal merge conflict. Inspect `git status`, resolve the affected files, stage those files, and run `git commit` to complete the merge. Then review the skill instructions, resource links, and any scripts before using the updated skills. A clean textual merge can still change a skill's behavior.

Use a normal merge when bringing the update branch back into your main branch. Preserve the subtree-generated commits and their metadata; squash-merging or rewriting them can lose the information needed for later subtree updates.

## Use the skills

Use [Skillshare](https://github.com/runkids/skillshare) to distribute this repository's edited skills to your AI tools. The existing directory layout works: configure the **repository root** as `sources.skills`, use `mode: merge` for per-skill links, and `target_naming: standard` for names such as `tdd`.

The [config example](skillshare.config.example.yaml) is ready to adapt for your machine. The root [`.skillignore`](.skillignore) enables original skills and leaves imported collections opt-in. After importing an upstream, enable the desired skill directories there, including any sibling skills they depend on.

See [Skillshare setup and skill requirements](docs/skillshare.md) for configuration, naming rules, selection examples, and preview commands. Keep using the subtree helper to merge upstream changes; Skillshare handles discovery and target links.

Keep upstream license and attribution files when sharing adapted material. Avoid installing an upstream-managed copy and your customized copy under the same skill name.

References: [Git subtree documentation](https://github.com/git/git/blob/master/contrib/subtree/git-subtree.adoc), [Matt Pocock's engineering collection](https://github.com/mattpocock/skills/tree/main/skills/engineering).
