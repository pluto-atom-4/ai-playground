import { apiGet, apiPost, apiPatch } from './backend';
import { API_ENDPOINTS, PAGINATION_DEFAULTS } from '@/lib/constants';
import { CandidatesResponseSchema, CandidateSchema } from '@/lib/validators';
import type { Candidate, CandidateStatus, CandidatesResponse } from '@/types';

/**
 * Candidates API service
 */

/**
 * Fetch candidates with optional filters
 */
export async function getCandidates(
  status?: CandidateStatus,
  jobId?: string,
  page = PAGINATION_DEFAULTS.PAGE,
  limit = PAGINATION_DEFAULTS.LIMIT,
): Promise<CandidatesResponse> {
  const params = new URLSearchParams();

  if (status) params.append('status', status);
  if (jobId) params.append('jobId', jobId);
  params.append('page', String(page));
  params.append('limit', String(Math.min(limit, PAGINATION_DEFAULTS.MAX_LIMIT)));

  const endpoint = `${API_ENDPOINTS.CANDIDATES}?${params.toString()}`;
  const response = await apiGet<unknown>(endpoint);

  // Validate response with Zod
  const parsed = CandidatesResponseSchema.parse(response);
  return parsed;
}

/**
 * Get a single candidate by ID
 */
export async function getCandidateById(candidateId: string): Promise<Candidate> {
  const endpoint = `${API_ENDPOINTS.CANDIDATES}/${candidateId}`;
  const response = await apiGet<unknown>(endpoint);

  // Validate response with Zod
  const parsed = CandidateSchema.parse(response);
  return parsed;
}

/**
 * Create a new candidate
 */
export async function createCandidate(candidate: {
  name: string;
  email: string;
  resumeUrl: string;
  extractedSkills: string[];
  currentStatus: CandidateStatus;
}): Promise<Candidate> {
  const response = await apiPost<unknown>(
    API_ENDPOINTS.CANDIDATES,
    candidate,
  );

  // Validate response with Zod
  const parsed = CandidateSchema.parse(response);
  return parsed;
}

/**
 * Update candidate status
 */
export async function updateCandidateStatus(
  candidateId: string,
  status: CandidateStatus,
  notes?: string,
): Promise<Candidate> {
  const endpoint = API_ENDPOINTS.CANDIDATE_STATUS(candidateId);
  const response = await apiPatch<unknown>(
    endpoint,
    { status, notes },
  );

  // Validate response with Zod
  const parsed = CandidateSchema.parse(response);
  return parsed;
}

/**
 * Fetch all candidates for a specific job (no pagination)
 */
export async function getCandidatesForJob(jobId: string): Promise<Candidate[]> {
  const params = new URLSearchParams();
  params.append('jobId', jobId);
  params.append('limit', String(PAGINATION_DEFAULTS.MAX_LIMIT));

  const endpoint = `${API_ENDPOINTS.CANDIDATES}?${params.toString()}`;
  const response = await apiGet<unknown>(endpoint);

  const parsed = CandidatesResponseSchema.parse(response);
  return parsed.data;
}

/**
 * Search candidates by status
 */
export async function getCandidatesByStatus(status: CandidateStatus): Promise<Candidate[]> {
  const params = new URLSearchParams();
  params.append('status', status);
  params.append('limit', String(PAGINATION_DEFAULTS.MAX_LIMIT));

  const endpoint = `${API_ENDPOINTS.CANDIDATES}?${params.toString()}`;
  const response = await apiGet<unknown>(endpoint);

  const parsed = CandidatesResponseSchema.parse(response);
  return parsed.data;
}

