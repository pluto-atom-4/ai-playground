import { MATCH_SCORE_THRESHOLDS } from '@/lib/constants';

/**
 * Match score calculation utilities
 */

export type MatchScoreBadgeColor = 'green' | 'yellow' | 'red';

/**
 * Get badge color based on match score
 */
export function getMatchScoreBadgeColor(matchScore: number): MatchScoreBadgeColor {
  if (matchScore > MATCH_SCORE_THRESHOLDS.GREEN) return 'green';
  if (matchScore >= MATCH_SCORE_THRESHOLDS.YELLOW) return 'yellow';
  return 'red';
}

/**
 * Get badge color class for Tailwind CSS
 */
export function getMatchScoreBadgeClass(matchScore: number): string {
  const color = getMatchScoreBadgeColor(matchScore);

  switch (color) {
    case 'green':
      return 'bg-match-green text-white';
    case 'yellow':
      return 'bg-match-yellow text-gray-900';
    case 'red':
      return 'bg-match-red text-white';
  }
}

/**
 * Format match score for display
 */
export function formatMatchScore(matchScore: number): string {
  return `${Math.round(matchScore)}%`;
}

/**
 * Calculate TF-IDF score for candidate skills vs job description keywords
 * Simplified implementation - full version should use proper NLP
 */
export function calculateTFIDFScore(
  candidateSkills: string[],
  jobKeywords: string[],
): number {
  if (candidateSkills.length === 0 || jobKeywords.length === 0) {
    return 0;
  }

  // Normalize strings for comparison
  const normalizedSkills = candidateSkills.map(s => s.toLowerCase());
  const normalizedKeywords = jobKeywords.map(k => k.toLowerCase());

  // Count matches
  const matches = normalizedSkills.filter(skill =>
    normalizedKeywords.some(keyword =>
      keyword.includes(skill) || skill.includes(keyword),
    ),
  ).length;

  // Calculate score as percentage
  const score = (matches / Math.max(normalizedSkills.length, normalizedKeywords.length)) * 100;

  return Math.min(100, Math.max(0, score));
}

/**
 * Calculate semantic similarity score (0-100)
 * Simplified implementation - full version should use embeddings
 */
export function calculateSemanticSimilarity(
  candidateProfile: {
    skills: string[];
    experience: number;
  },
  jobProfile: {
    requiredSkills: string[];
    yearsRequired: number;
  },
): number {
  let score = 0;

  // Skills match (60% weight)
  const skillsScore = calculateTFIDFScore(
    candidateProfile.skills,
    jobProfile.requiredSkills,
  );
  score += skillsScore * 0.6;

  // Experience match (40% weight)
  const experienceMatch = candidateProfile.experience >= jobProfile.yearsRequired ? 100 : 0;
  score += experienceMatch * 0.4;

  return Math.min(100, Math.max(0, score));
}

/**
 * Rank candidates by match score
 */
export function rankCandidates<T extends { matchScore: number }>(
  candidates: T[],
  descending = true,
): T[] {
  return [...candidates].sort((a, b) =>
    descending ? b.matchScore - a.matchScore : a.matchScore - b.matchScore,
  );
}

/**
 * Filter candidates by match score threshold
 */
export function filterCandidatesByMatchScore(
  candidates: Array<{ matchScore: number }>,
  minScore: number,
): Array<{ matchScore: number }> {
  return candidates.filter(candidate => candidate.matchScore >= minScore);
}

/**
 * Calculate average match score
 */
export function calculateAverageMatchScore(
  candidates: Array<{ matchScore: number }>,
): number {
  if (candidates.length === 0) return 0;

  const total = candidates.reduce((sum, candidate) => sum + candidate.matchScore, 0);
  return Math.round(total / candidates.length);
}

/**
 * Get match score statistics
 */
export function getMatchScoreStats(candidates: Array<{ matchScore: number }>) {
  if (candidates.length === 0) {
    return {
      min: 0,
      max: 0,
      average: 0,
      median: 0,
    };
  }

  const scores = candidates.map(c => c.matchScore).sort((a, b) => a - b);

  return {
    min: scores[0],
    max: scores[scores.length - 1],
    average: calculateAverageMatchScore(candidates),
    median: scores[Math.floor(scores.length / 2)],
  };
}

