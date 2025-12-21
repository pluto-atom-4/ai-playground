'use client';

import { useState, useCallback } from 'react';
import { semanticSearchCached } from '@/services/search-api';
import type { SearchResult } from '@/types';

/**
 * Hook for semantic search with loading and error handling
 */

export function useSemanticSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [query, setQuery] = useState('');

  const search = useCallback(
    async (searchQuery: string, jobId: string, limit = 50) => {
      setIsLoading(true);
      setError(null);
      setQuery(searchQuery);

      try {
        const searchResults = await semanticSearchCached(
          searchQuery,
          jobId,
          limit,
        );
        setResults(searchResults);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Search failed');
        setError(error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clearSearch = useCallback(() => {
    setResults([]);
    setQuery('');
    setError(null);
  }, []);

  return {
    results,
    isLoading,
    error,
    query,
    search,
    clearSearch,
  };
}

