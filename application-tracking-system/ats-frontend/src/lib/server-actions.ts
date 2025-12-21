'use server';

import { CACHE_REVALIDATE_WINDOW, ENABLE_CACHING } from '@/lib/constants';
import { getCandidatesForJob, updateCandidateStatus } from '@/services/candidates-api';
import type { Candidate, CandidateStatus } from '@/types';

/**
 * Server Actions for candidate management with caching
 */

/**
 * Fetch candidates for a job with optional caching
 * Uses unstable_cache for heavy NLP ranking results
 */
export async function fetchCandidatesForJobAction(jobDescriptionId: string): Promise<Candidate[]> {
  if (!ENABLE_CACHING) {
    return getCandidatesForJob(jobDescriptionId);
  }

  // Import unstable_cache dynamically for Next.js 16
  const { unstable_cache } = await import('next/cache');

  const getCachedCandidates = unstable_cache(
    async (jobId: string) => {
      return getCandidatesForJob(jobId);
    },
    ['candidates', jobDescriptionId],
    { revalidate: CACHE_REVALIDATE_WINDOW },
  );

  return getCachedCandidates(jobDescriptionId);
}

/**
 * Update candidate status with cache invalidation
 */
export async function updateCandidateStatusAction(
  candidateId: string,
  status: CandidateStatus,
  notes?: string,
): Promise<Candidate> {
  const updated = await updateCandidateStatus(candidateId, status, notes);

  // Invalidate related caches on update
  if (ENABLE_CACHING) {
    const { revalidatePath } = await import('next/cache');
    revalidatePath('/dashboard');
    revalidatePath('/pipeline');
  }

  return updated;
}

/**
 * Manual cache invalidation for dashboard
 */
export async function invalidateCandidatesCacheAction(): Promise<void> {
  if (!ENABLE_CACHING) return;

  const { revalidatePath } = await import('next/cache');
  revalidatePath('/dashboard');
  revalidatePath('/pipeline');
}

