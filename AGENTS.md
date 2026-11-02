# Personal skills repository

This repository holds original skills and editable copies from multiple upstreams.

- Author original skills in `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter. Keep supporting files beside the skill.
- Configure external repositories in `upstreams.json`. Each source is imported into `upstreams/<source-name>/` with Git subtree; these are normal tracked files that can be customized directly.
- Use `python3 scripts/upstream.py sync <source-name>` to import or update a selected source. It creates local Git commits and requires a clean working tree with an existing commit.
- Preserve the subtree commit metadata and upstream directory structure so later merges retain their baseline. Do not replace customized files by copying a fresh upstream snapshot over them.
- Resolve upstream conflicts by considering both the local customization and the upstream intent. Review changed skill instructions and referenced resources after a merge.
- Keep upstream license and attribution files. When selecting skills for installation, inspect dependencies on sibling skills and preserve relative resource paths.
- Credit every original source in `INVENTORY.md`, including original author, repository, skill path, applicable license, and reviewed upstream revision. Separate requested skills from supporting dependencies.
- Each selected imported skill must carry `UPSTREAM.md` and the applicable license text (`LICENSE.upstream` here) so attribution survives individual copies. Preserve existing credits and notices. Record local changes separately from original authorship; refresh provenance and dependency selections after upstream merges.
- Install selected skill directories from this repository. Avoid exposing multiple copies with the same skill name to an agent.
- Skillshare uses this repository root as `sources.skills`; keep both `skills/` and `upstreams/` beneath it. Use the root `.skillignore` to select imported skills. Its patterns match skill directories, not `SKILL.md` filenames.
- The Skillshare config example uses `mode: merge` and `target_naming: standard`. Keep each enabled skill's name unique and equal to its immediate folder name, using at most 64 lowercase letters, digits, and single hyphens. Include a meaningful description and instructions.
- Use the subtree helper for upstream updates, then `skillshare sync -g` to refresh target links. Skillshare's `update` command does not consume `upstreams.json` or merge these subtrees. Its `merge` sync mode means per-skill links, not Git content merging.

See `INVENTORY.md` for the selected skills and credits, `README.md` for the update workflow, and `docs/skillshare.md` for the Skillshare configuration and format requirements.
