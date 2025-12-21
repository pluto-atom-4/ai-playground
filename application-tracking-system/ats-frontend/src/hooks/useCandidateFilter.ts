'use client';

import { useMemo, useState } from 'react';
import { filterCandidatesByMatchScore, rankCandidates } from '@/lib/match-score';
import type { Candidate, CandidateStatus } from '@/types';

/**
 * Hook for filtering and sorting candidates
 */

export function useCandidateFilter(candidates: Candidate[]) {
  const [statusFilter, setStatusFilter] = useState<CandidateStatus | 'All'>('All');
  const [minMatchScore, setMinMatchScore] = useState(0);
  const [sortBy, setSortBy] = useState<'match' | 'name' | 'date'>('match');

  const filtered = useMemo(() => {
    let result = [...candidates];

    // Filter by status
    if (statusFilter !== 'All') {
      result = result.filter(c => c.currentStatus === statusFilter);
    }

    // Filter by match score
    result = filterCandidatesByMatchScore(result, minMatchScore);

    // Sort
    switch (sortBy) {
      case 'match':
        result = rankCandidates(result, true); // descending
        break;
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'date':
        result.sort((a, b) => {
          const dateA = new Date(a.createdAt || 0).getTime();
          const dateB = new Date(b.createdAt || 0).getTime();
          return dateB - dateA;
        });
        break;
    }

    return result;
  }, [candidates, statusFilter, minMatchScore, sortBy]);

  const stats = useMemo(() => {
    const total = candidates.length;
    const byStatus = candidates.reduce((acc, c) => {
      acc[c.currentStatus] = (acc[c.currentStatus] || 0) + 1;
      return acc;
    }, {} as Record<CandidateStatus, number>);

    const avgMatchScore = candidates.length > 0
      ? Math.round(candidates.reduce((sum, c) => sum + c.matchScore, 0) / candidates.length)
      : 0;

    return {
      total,
      byStatus,
      avgMatchScore,
      filtered: filtered.length,
    };
  }, [candidates, filtered]);

  return {
    filtered,
    stats,
    filters: {
      statusFilter,
      setStatusFilter,
      minMatchScore,
      setMinMatchScore,
      sortBy,
      setSortBy,
    },
  };
}

