import { API_BASE, API_TIMEOUT, API_RETRY_ATTEMPTS } from '@/lib/constants';

/**
 * Base API utility for all backend communication
 */

export interface FetchOptions extends RequestInit {
  timeout?: number;
  retries?: number;
}

/**
 * Enhanced fetch with timeout and retry logic
 */
export async function fetchWithRetry<T>(
  url: string,
  options: FetchOptions = {},
): Promise<T> {
  const { timeout = API_TIMEOUT, retries = API_RETRY_ATTEMPTS, ...fetchOptions } = options;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      return await response.json() as T;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on last attempt
      if (attempt < retries - 1) {
        // Exponential backoff: 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }
  }

  throw lastError || new Error('Fetch failed after retries');
}

/**
 * Construct full API URL
 */
export function getApiUrl(endpoint: string): string {
  return `${API_BASE}${endpoint}`;
}

/**
 * Make GET request to backend
 */
export async function apiGet<T>(endpoint: string, options?: FetchOptions): Promise<T> {
  return fetchWithRetry<T>(getApiUrl(endpoint), {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });
}

/**
 * Make POST request to backend
 */
export async function apiPost<T>(
  endpoint: string,
  data?: Record<string, unknown>,
  options?: FetchOptions,
): Promise<T> {
  return fetchWithRetry<T>(getApiUrl(endpoint), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });
}

/**
 * Make PATCH request to backend
 */
export async function apiPatch<T>(
  endpoint: string,
  data?: Record<string, unknown>,
  options?: FetchOptions,
): Promise<T> {
  return fetchWithRetry<T>(getApiUrl(endpoint), {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });
}

/**
 * Make POST request with FormData (for file uploads)
 */
export async function apiPostFormData<T>(
  endpoint: string,
  formData: FormData,
  options?: FetchOptions,
): Promise<T> {
  return fetchWithRetry<T>(getApiUrl(endpoint), {
    method: 'POST',
    body: formData,
    ...options,
  });
}

