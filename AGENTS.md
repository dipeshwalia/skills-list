# Personal skills repository

This repository holds original skills and editable copies from multiple upstreams.

- Author original skills in `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter. Keep supporting files beside the skill.
- Configure external repositories in `upstreams.json`. Each source is imported into `upstreams/<source-name>/` with Git subtree; these are normal tracked files that can be customized directly.
- Use `python3 scripts/upstream.py sync <source-name>` to import or update a selected source. It creates local Git commits and requires a clean working tree with an existing commit.
- Preserve the subtree commit metadata and upstream directory structure so later merges retain their baseline. Do not replace customized files by copying a fresh upstream snapshot over them.
- Resolve upstream conflicts by considering both the local customization and the upstream intent. Review changed skill instructions and referenced resources after a merge.
- Keep upstream license and attribution files. When selecting skills for installation, inspect dependencies on sibling skills and preserve relative resource paths.
- Install selected skill directories from this repository. Avoid exposing multiple copies with the same skill name to an agent.

See `README.md` for source configuration and the update workflow.
