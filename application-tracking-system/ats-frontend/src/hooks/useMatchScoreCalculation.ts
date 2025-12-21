'use client';

import { useMemo } from 'react';
import {
  calculateSemanticSimilarity,
  getMatchScoreBadgeColor,
  getMatchScoreBadgeClass,
  formatMatchScore,
} from '@/lib/match-score';

/**
 * Hook for match score calculations and formatting
 */

export interface MatchScoreInput {
  skills: string[];
  experience: number;
}

export interface MatchScoreJob {
  requiredSkills: string[];
  yearsRequired: number;
}

export function useMatchScoreCalculation(
  candidateProfile: MatchScoreInput,
  jobProfile: MatchScoreJob,
) {
  const score = useMemo(() => {
    return calculateSemanticSimilarity(candidateProfile, jobProfile);
  }, [candidateProfile, jobProfile]);

  const color = useMemo(() => {
    return getMatchScoreBadgeColor(score);
  }, [score]);

  const badgeClass = useMemo(() => {
    return getMatchScoreBadgeClass(score);
  }, [score]);

  const formattedScore = useMemo(() => {
    return formatMatchScore(score);
  }, [score]);

  return {
    score,
    color,
    badgeClass,
    formattedScore,
  };
}

