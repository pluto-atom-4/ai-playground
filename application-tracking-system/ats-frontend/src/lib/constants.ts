/**
 * Constants for the ATS frontend application
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000', 10);

export const API_RETRY_ATTEMPTS = parseInt(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS || '3', 10);

export const ENABLE_CACHING = process.env.NEXT_PUBLIC_ENABLE_CACHING === 'true';

export const CACHE_REVALIDATE_WINDOW = 3600; // 1 hour in seconds

export const MATCH_SCORE_THRESHOLDS = {
  GREEN: 85,     // > 85%
  YELLOW: 60,    // 60-84%
  RED: 0,        // < 60%
};

export const CANDIDATE_STATUSES = ['Applied', 'Screening', 'Interview', 'Hired', 'Rejected'] as const;

export const PAGINATION_DEFAULTS = {
  PAGE: 1,
  LIMIT: 20,
  MAX_LIMIT: 100,
};

export const API_ENDPOINTS = {
  PARSE_RESUME: '/api/parse-resume',
  SEMANTIC_SEARCH: '/api/semantic-search',
  CANDIDATES: '/api/candidates',
  CANDIDATE_STATUS: (id: string) => `/api/candidates/${id}/status`,
};

