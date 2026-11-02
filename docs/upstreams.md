# Managing upstream skills

Run these commands from the repository root. The scripts preserve Git subtree history so upstream changes can merge with your local edits.

## Start

Requires Python 3 and Git with `git subtree`. This repository is already initialized and includes its upstream import history. Use a Git clone when moving it to another machine so that history, including the subtree merge baselines, travels with the files. Commit or stash changes before importing or updating a source.

`origin` points to the personal repository, `dipeshwalia/skills-list`. Upstream sources are configured separately and do not need to be added as Git remotes.

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

Update every imported parent repository from its configured ref:

```sh
./scripts/sync-upstreams.sh --dry-run
./scripts/sync-upstreams.sh
```

The script works from any working directory when invoked by its path. It reads `upstreams.json`; `origin`, when configured, is your personal repository, not these original sources. For Matt Pocock's source, the configured ref is `main`, so sync fetches its latest commit. Pinned tags or commits stay pinned.

To choose sources, run `./scripts/sync-upstreams.sh mattpocock` or pass several source names. With no names (or with `--all`), only already-imported sources are updated; configured sources that are not imported are skipped. Name a source explicitly to import it. The equivalent Python command is `python3 scripts/upstream.py sync --all`.

Commit your current work first, including any new files. Use a branch to review an update:

```sh
git switch -c update-mattpocock
./scripts/sync-upstreams.sh mattpocock
git diff main...HEAD -- upstreams/mattpocock
```

If both sides edit the same content, Git leaves a normal merge conflict. Inspect `git status`, resolve the affected files, stage those files, and run `git commit` to complete the merge. Then review the skill instructions, resource links, and any scripts before using the updated skills. A clean textual merge can still change a skill's behavior.

Sources sync sequentially. A failure stops the remaining updates; earlier successful sources remain committed. The script refuses a dirty working tree or an unfinished Git operation. `--dry-run` prints the planned commands without fetching or changing files.

Attribution and license files remain part of the normal Git merge. After reviewing an update, refresh [the inventory](../INVENTORY.md), each selected skill's `UPSTREAM.md`, and its `LICENSE.upstream` if the applicable license changed. Sync does not automatically mark new content as reviewed, enable new skills, push commits, or run Skillshare.

Run `python3 -m unittest discover -s tests -v` to verify the helper against temporary local Git repositories; the tests need no network access.

Use a normal merge when bringing the update branch back into your main branch. Preserve the subtree-generated commits and their metadata; squash-merging or rewriting them can lose the information needed for later subtree updates.

Reference: [Git subtree documentation](https://github.com/git/git/blob/master/contrib/subtree/git-subtree.adoc).
