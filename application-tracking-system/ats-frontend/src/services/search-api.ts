import { apiPost } from './backend';
import { API_ENDPOINTS } from '@/lib/constants';
import { SemanticSearchResponseSchema } from '@/lib/validators';
import type { SearchResult } from '@/types';

/**
 * Semantic search API service
 */

/**
 * Search for candidates using natural language query
 */
export async function semanticSearch(
  query: string,
  jobDescriptionId: string,
  limit = 50,
): Promise<SearchResult[]> {
  const response = await apiPost<unknown>(
    API_ENDPOINTS.SEMANTIC_SEARCH,
    {
      query,
      jobDescriptionId,
      limit,
    },
  );

  // Validate response with Zod
  const parsed = SemanticSearchResponseSchema.parse(response);
  return parsed.results;
}

/**
 * Search with caching support (for heavy queries)
 */
export async function semanticSearchCached(
  query: string,
  jobDescriptionId: string,
  limit = 50,
  cacheKey?: string,
): Promise<SearchResult[]> {
  // Cache key for localStorage (optional)
  const key = cacheKey || `search-${jobDescriptionId}-${query}`;

  // Check localStorage cache (short-term, 5 minutes)
  const cached = typeof window !== 'undefined' ? localStorage.getItem(key) : null;
  if (cached) {
    const cacheData = JSON.parse(cached);
    const isExpired = Date.now() - cacheData.timestamp > 5 * 60 * 1000; // 5 minutes
    if (!isExpired) {
      return cacheData.results;
    }
  }

  // Fetch fresh results
  const results = await semanticSearch(query, jobDescriptionId, limit);

  // Store in localStorage cache
  if (typeof window !== 'undefined') {
    localStorage.setItem(
      key,
      JSON.stringify({
        results,
        timestamp: Date.now(),
      }),
    );
  }

  return results;
}

