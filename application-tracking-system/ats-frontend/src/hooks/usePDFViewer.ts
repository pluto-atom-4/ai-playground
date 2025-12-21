'use client';

import { useState, useCallback } from 'react';

/**
 * Hook for PDF viewer state management and interaction
 */

export function usePDFViewer() {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [scale, setScale] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [highlightedText, setHighlightedText] = useState<Set<string>>(new Set());

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setTotalPages(numPages);
    setIsLoading(false);
  }, []);

  const onDocumentLoadError = useCallback((error: Error) => {
    setError(error);
    setIsLoading(false);
  }, []);

  const nextPage = useCallback(() => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  }, [totalPages]);

  const prevPage = useCallback(() => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  }, []);

  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.min(Math.max(page, 1), totalPages));
  }, [totalPages]);

  const zoomIn = useCallback(() => {
    setScale(prev => Math.min(prev + 0.1, 2));
  }, []);

  const zoomOut = useCallback(() => {
    setScale(prev => Math.max(prev - 0.1, 0.5));
  }, []);

  const toggleHighlight = useCallback((text: string) => {
    setHighlightedText(prev => {
      const newSet = new Set(prev);
      if (newSet.has(text)) {
        newSet.delete(text);
      } else {
        newSet.add(text);
      }
      return newSet;
    });
  }, []);

  const clearHighlights = useCallback(() => {
    setHighlightedText(new Set());
  }, []);

  return {
    currentPage,
    totalPages,
    scale,
    isLoading,
    error,
    highlightedText,
    onDocumentLoadSuccess,
    onDocumentLoadError,
    nextPage,
    prevPage,
    goToPage,
    zoomIn,
    zoomOut,
    toggleHighlight,
    clearHighlights,
  };
}

