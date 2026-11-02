import manifest from './sources.json' with { type: 'json' }

export interface Source {
  /** Upstream source in owner/repo or owner/repo/sub/path form. */
  source: string
  /** Invocation prefix: Workflow becomes /workflow-<skill-name>. */
  category: string
  /** Skill names to pick; omitted means every canonical skill in the source. */
  skills?: string[]
}

/** Edit sources.json; both TypeScript consumers and the package builder read it. */
export const sources: Source[] = manifest
