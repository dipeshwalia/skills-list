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

Keep the imported directory at the same path. After editing it, rebuild the category-prefixed packages and commit both the source and generated changes:

```sh
python3 scripts/build-skills.py
python3 scripts/build-skills.py --check
```

The installed `workflow-tdd` package is generated from the canonical `tdd` directory. Its folder and frontmatter name both use the category prefix. The builder preserves resources, updates selected sibling links, and carries original-source attribution into each package.

Do not edit a generated package directly. The builder checks saved hashes and refuses to replace manual changes. Move such changes into the canonical source, preserve any work you need, restore the generated copy from Git, then rebuild. Original skills that are not generated can live under `skills/<category>-<name>/` with matching `name` and `description` frontmatter.

Imported maintainer files and install scripts describe their original projects. Do not follow their instructions or run scripts such as `scripts/link-skills.sh`; those bypass this collection's selection and distribution workflow. Leave these files intact for future subtree merges.

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

`upstreams.json` records where updates come from; subtree commits record the exact upstream revisions imported. A source stays at its imported version until you explicitly sync it.

After importing, give each selected skill an `UPSTREAM.md` that names the imported revision and a verbatim `LICENSE.upstream`. Then add one project record to [sources.json](../sources.json) with the original author, the license file, name, and copyright as the file states them, and `reviewed` set to the imported revision. List each selected skill with its purpose, category, and role (`requested` or `supporting`). Record the companions it calls in `requires`, and optional pointers in `recommends`. The category becomes the invocation prefix, for example `Workflow` and `improve` become `/workflow-improve`. [sources.ts](../sources.ts) exports the same records through typed interfaces.

Run `python3 scripts/build-skills.py`. It validates the records, rejects a selection that leaves out a required companion, and generates the packages and the attribution tables in the README, [the inventory](../INVENTORY.md), and [the catalog](../skills/README.md). Edit the records, not the generated tables. The root `.skillignore` includes only `skills/`, so upstream copies do not create duplicate invocations.

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

Sources sync sequentially. A failure stops the remaining updates; earlier successful sources remain committed. The script refuses a dirty working tree or an unfinished Git operation. `--dry-run` prints the planned merge commands without fetching or changing files.

Updates follow one sequence: **merge upstreams → review changes and provenance → build installed packages**.

1. **Merge.** Sync merges and commits the upstream changes, then prints each merged revision. It publishes nothing: the generated packages, which Skillshare links into your agents, keep serving the reviewed versions.
2. **Review.** Read the merged skill instructions, resource links, scripts, and license notices. Refresh each selected skill's `UPSTREAM.md` with the merged revision and any local-change notes, and its `LICENSE.upstream` if the license changed. Then set the project's `reviewed` revision in [sources.json](../sources.json) to the merged revision. Update its skill records if selections or companions changed.
3. **Build.** Run `python3 scripts/build-skills.py`. It refuses to publish while a project's `reviewed` revision differs from the merged revision, or while a selected skill's `UPSTREAM.md` does not name it. Commit the generated packages, tables, and `skills/.generated.json` with the review changes, then run `skillshare sync -g`.

Sync does not mark content as reviewed, change the inventory records, publish packages, push commits, or run Skillshare.

Run `python3 -m unittest discover -s tests -v` to verify the helper against temporary local Git repositories; the tests need no network access.

Use a normal merge when bringing the update branch back into your main branch. Preserve the subtree-generated commits and their metadata; squash-merging or rewriting them can lose the information needed for later subtree updates.

Reference: [Git subtree documentation](https://github.com/git/git/blob/master/contrib/subtree/git-subtree.adoc).
