import { apiPostFormData } from './backend';
import { API_ENDPOINTS } from '@/lib/constants';
import { ParsedResumeSchema } from '@/lib/validators';
import type { ParsedResume } from '@/types';

/**
 * Resume parsing API service
 */

/**
 * Parse a resume file and extract structured data
 */
export async function parseResumeFile(file: File): Promise<ParsedResume> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiPostFormData<unknown>(
    API_ENDPOINTS.PARSE_RESUME,
    formData,
  );

  // Validate response with Zod
  const parsed = ParsedResumeSchema.parse(response);
  return parsed;
}

/**
 * Parse multiple resume files in batch
 */
export async function parseResumeFileBatch(files: File[]): Promise<ParsedResume[]> {
  const promises = files.map(file => parseResumeFile(file));
  return Promise.all(promises);
}

