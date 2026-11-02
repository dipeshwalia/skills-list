import manifest from './sources.json' with { type: 'json' }

/** One original author's project, its credits, its reviewed revision, and the skills selected from it. */
export interface Source {
  /** Project in owner/repo or owner/repo/sub/path form. */
  source: string
  /** Original author credited for every skill in this project. */
  author: string
  /** License file (relative to the project), license name, and copyright holder as the file states them. */
  license: { file: string; name: string; copyright: string }
  /** Upstream commit whose changes and provenance were reviewed. The builder publishes nothing newer. */
  reviewed: string
  /** Default category for the skills below. Workflow becomes the /workflow-<skill-name> prefix. */
  category?: string
  skills: SkillRecord[]
}

/** A selected skill and its relationships. */
export interface SkillRecord {
  name: string
  /** One-line purpose shown in the generated catalogs. */
  purpose: string
  /** Overrides the project's default category. */
  category?: string
  /** requested (default) or supporting; a supporting skill must be required or recommended by another. */
  role?: 'requested' | 'supporting'
  /** Companions that must also be selected; the builder rejects incomplete selections. */
  requires?: string[]
  /** Optional companions; they need not be selected. */
  recommends?: string[]
  /** Development-only paths, relative to the skill, to leave out of its package. */
  exclude?: string[]
}

/** Edit sources.json; the builder and TypeScript consumers read the same records. */
export const sources = manifest as Source[]
