import { z } from 'zod';

/**
 * Zod validation schemas for API responses and requests
 */

export const CandidateStatusSchema = z.enum([
  'Applied',
  'Screening',
  'Interview',
  'Hired',
  'Rejected',
]);

export const CandidateSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  matchScore: z.number().min(0).max(100),
  extractedSkills: z.array(z.string()),
  resumeUrl: z.string().url(),
  currentStatus: CandidateStatusSchema,
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  notes: z.string().optional(),
});

export const ParsedResumeSchema = z.object({
  id: z.string(),
  candidateName: z.string(),
  email: z.string().email(),
  skills: z.array(z.string()),
  experience: z.array(z.object({
    role: z.string(),
    company: z.string(),
    years: z.number(),
    description: z.string().optional(),
    startDate: z.string().optional(),
    endDate: z.string().optional(),
  })),
  education: z.array(z.object({
    degree: z.string(),
    institution: z.string(),
    year: z.number().optional(),
    field: z.string().optional(),
  })),
  extractedText: z.string(),
});

export const SearchResultSchema = z.object({
  candidateId: z.string(),
  candidateName: z.string(),
  matchScore: z.number().min(0).max(100),
  relevantSkills: z.array(z.string()),
  matchedKeywords: z.record(z.number()).optional(),
});

export const SemanticSearchResponseSchema = z.object({
  results: z.array(SearchResultSchema),
  queryTime: z.string().optional(),
});

export const CandidatesResponseSchema = z.object({
  data: z.array(CandidateSchema),
  total: z.number(),
  page: z.number(),
  limit: z.number(),
});

export const UpdateCandidateStatusSchema = z.object({
  status: CandidateStatusSchema,
  notes: z.string().optional(),
});

export const UpdateCandidateStatusRequestSchema = z.object({
  status: z.string(),
  notes: z.string().optional(),
});

// Type exports for use in components
export type Candidate = z.infer<typeof CandidateSchema>;
export type ParsedResume = z.infer<typeof ParsedResumeSchema>;
export type SearchResult = z.infer<typeof SearchResultSchema>;
export type CandidateStatus = z.infer<typeof CandidateStatusSchema>;
export type UpdateCandidateStatus = z.infer<typeof UpdateCandidateStatusSchema>;

