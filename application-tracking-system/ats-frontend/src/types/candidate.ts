/**
 * Core candidate types and interfaces for the ATS application
 */

export type CandidateStatus = 'Applied' | 'Screening' | 'Interview' | 'Hired' | 'Rejected';

export interface Candidate {
  id: string;
  name: string;
  email: string;
  matchScore: number; // 0-100
  extractedSkills: string[];
  resumeUrl: string;
  currentStatus: CandidateStatus;
  createdAt?: Date;
  updatedAt?: Date;
  notes?: string;
}

export interface ParsedResume {
  id: string;
  candidateName: string;
  email: string;
  skills: string[];
  experience: Experience[];
  education: Education[];
  extractedText: string;
}

export interface Experience {
  role: string;
  company: string;
  years: number;
  description?: string;
  startDate?: string;
  endDate?: string;
}

export interface Education {
  degree: string;
  institution: string;
  year?: number;
  field?: string;
}

export interface SearchResult {
  candidateId: string;
  candidateName: string;
  matchScore: number;
  relevantSkills: string[];
  matchedKeywords?: Record<string, number>;
}

export interface CandidatesResponse {
  data: Candidate[];
  total: number;
  page: number;
  limit: number;
}

