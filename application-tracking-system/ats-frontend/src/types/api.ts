/**
 * API-related types and interfaces
 */

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface UpdateCandidateStatusRequest {
  status: string;
  notes?: string;
}

export interface SemanticSearchRequest {
  query: string;
  jobDescriptionId: string;
  limit?: number;
}

export interface SemanticSearchResponse {
  results: Array<{
    candidateId: string;
    candidateName: string;
    matchScore: number;
    relevantSkills: string[];
    matchedKeywords?: Record<string, number>;
  }>;
  queryTime?: string;
}

