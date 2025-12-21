'use client';

import { useOptimistic, useState } from 'react';
import { updateCandidateStatusAction } from '@/lib/server-actions';
import type { Candidate, CandidateStatus } from '@/types';

/**
 * Hook for optimistic candidate status updates (React 19.2)
 * Updates UI immediately while server request processes in background
 */

export function useOptimisticStatus(initialCandidate: Candidate) {
  const [optimisticCandidate, setOptimisticCandidate] = useOptimistic(
    initialCandidate,
    (state, newStatus: CandidateStatus) => ({
      ...state,
      currentStatus: newStatus,
    }),
  );

  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const updateStatus = async (newStatus: CandidateStatus, notes?: string) => {
    setIsPending(true);
    setError(null);

    try {
      // Optimistic UI update - immediate
      setOptimisticCandidate(newStatus);

      // Server action - async
      await updateCandidateStatusAction(initialCandidate.id, newStatus, notes);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update status');
      setError(error);
      // Reset optimistic state on error
      setOptimisticCandidate(initialCandidate.currentStatus);
    } finally {
      setIsPending(false);
    }
  };

  return {
    candidate: optimisticCandidate,
    isPending,
    error,
    updateStatus,
  };
}

