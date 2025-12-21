/**
 * Skill extraction and mapping utilities
 */

/**
 * Common synonyms for skill normalization
 */
const SKILL_SYNONYMS: Record<string, string> = {
  js: 'javascript',
  js: 'javascript',
  ts: 'typescript',
  py: 'python',
  rb: 'ruby',
  go: 'golang',
  cpp: 'c++',
  cs: 'c#',
  'node.js': 'nodejs',
  'node': 'nodejs',
  'react.js': 'react',
  'vue.js': 'vue',
  'angular.js': 'angular',
  'express.js': 'express',
  'fast api': 'fastapi',
  'psql': 'postgresql',
  'postgres': 'postgresql',
  'mongo': 'mongodb',
  'mysql': 'mysql',
  'nosql': 'database',
  'sql': 'database',
  'rest api': 'rest',
  'graphql api': 'graphql',
  'docker': 'docker',
  'kubernetes': 'kubernetes',
  'k8s': 'kubernetes',
  'aws': 'aws',
  'gcp': 'google cloud',
  'azure': 'azure',
  'ci/cd': 'cicd',
};

/**
 * Normalize skill name (lowercase, trim, apply synonyms)
 */
export function normalizeSkill(skill: string): string {
  let normalized = skill.trim().toLowerCase();

  // Apply synonyms
  if (SKILL_SYNONYMS[normalized]) {
    normalized = SKILL_SYNONYMS[normalized];
  }

  return normalized;
}

/**
 * Normalize array of skills
 */
export function normalizeSkills(skills: string[]): string[] {
  return [...new Set(skills.map(normalizeSkill))];
}

/**
 * Extract unique skills from raw text
 */
export function extractSkillsFromText(text: string): string[] {
  // Common programming languages and frameworks
  const skillPatterns = [
    'javascript',
    'typescript',
    'python',
    'java',
    'c\\+\\+',
    'c#',
    'ruby',
    'php',
    'golang',
    'rust',
    'swift',
    'kotlin',
    'react',
    'vue',
    'angular',
    'svelte',
    'express',
    'fastapi',
    'django',
    'flask',
    'spring',
    'rails',
    'node\\.?js',
    'mongodb',
    'postgresql',
    'mysql',
    'redis',
    'docker',
    'kubernetes',
    'aws',
    'azure',
    'gcp',
    'git',
    'rest',
    'graphql',
    'sql',
    'nosql',
    'html',
    'css',
    'sass',
    'webpack',
    'vite',
  ];

  const regex = new RegExp(`\\b(${skillPatterns.join('|')})\\b`, 'gi');
  const matches = text.match(regex) || [];

  return normalizeSkills(matches);
}

/**
 * Map extracted skills to standardized skill categories
 */
export function categorizeSkills(skills: string[]): Record<string, string[]> {
  const categories: Record<string, string[]> = {
    languages: [],
    frontend: [],
    backend: [],
    databases: [],
    tools: [],
    cloud: [],
    other: [],
  };

  const categorization: Record<string, string> = {
    // Languages
    javascript: 'languages',
    typescript: 'languages',
    python: 'languages',
    java: 'languages',
    'c++': 'languages',
    'c#': 'languages',
    ruby: 'languages',
    php: 'languages',
    golang: 'languages',
    rust: 'languages',
    swift: 'languages',
    kotlin: 'languages',

    // Frontend
    react: 'frontend',
    vue: 'frontend',
    angular: 'frontend',
    svelte: 'frontend',
    html: 'frontend',
    css: 'frontend',
    sass: 'frontend',

    // Backend
    express: 'backend',
    fastapi: 'backend',
    django: 'backend',
    flask: 'backend',
    spring: 'backend',
    rails: 'backend',
    nodejs: 'backend',

    // Databases
    mongodb: 'databases',
    postgresql: 'databases',
    mysql: 'databases',
    redis: 'databases',
    database: 'databases',

    // Tools
    docker: 'tools',
    kubernetes: 'tools',
    git: 'tools',
    webpack: 'tools',
    vite: 'tools',

    // Cloud
    aws: 'cloud',
    'google cloud': 'cloud',
    azure: 'cloud',
    gcp: 'cloud',
  };

  for (const skill of skills) {
    const normalized = normalizeSkill(skill);
    const category = categorization[normalized] || 'other';
    if (!categories[category].includes(normalized)) {
      categories[category].push(normalized);
    }
  }

  return categories;
}

/**
 * Calculate skill match percentage between candidate skills and required skills
 */
export function calculateSkillMatchPercentage(
  candidateSkills: string[],
  requiredSkills: string[],
): number {
  if (requiredSkills.length === 0) return 100;

  const normalized = {
    candidate: normalizeSkills(candidateSkills),
    required: normalizeSkills(requiredSkills),
  };

  const matches = normalized.required.filter(skill =>
    normalized.candidate.includes(skill),
  ).length;

  return (matches / normalized.required.length) * 100;
}

/**
 * Find missing skills (required but not in candidate profile)
 */
export function findMissingSkills(
  candidateSkills: string[],
  requiredSkills: string[],
): string[] {
  const normalized = {
    candidate: normalizeSkills(candidateSkills),
    required: normalizeSkills(requiredSkills),
  };

  return normalized.required.filter(skill =>
    !normalized.candidate.includes(skill),
  );
}

/**
 * Find additional skills (candidate has but not required)
 */
export function findAdditionalSkills(
  candidateSkills: string[],
  requiredSkills: string[],
): string[] {
  const normalized = {
    candidate: normalizeSkills(candidateSkills),
    required: normalizeSkills(requiredSkills),
  };

  return normalized.candidate.filter(skill =>
    !normalized.required.includes(skill),
  );
}

