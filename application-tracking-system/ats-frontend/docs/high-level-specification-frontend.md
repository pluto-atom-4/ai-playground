# Frontend specifications on ATS

To implement a high-performance Applicant Tracking System (ATS) in December 2025, follow these frontend specifications optimized for Next.js 16.1 and React 19.2.

## 1. Core Frontend Specifications (Next.js 16)

* **The "React Compiler" Baseline**: Ensure the **React Compiler** is enabled in your next.config.ts. This eliminates the need for manual memoization (useMemo, useCallback) when filtering large candidate datasets Next.js Docs.
* **Data Strategy**: Use Server Actions for all candidate status updates and use cache directives for heavy NLP ranking results. This ensures your ranking scores are computed once and reused across recruiter sessions Next.js Blog.
* **Security**: You must use version **16.1** or higher to patch **CVE-2025-55182** (React2Shell).

## 2. Essential ATS Features to Build

**A. Recruiter Dashboard (High-Density Overview)**

* **Metric Tiles**: Real-time summary of "New Applicants," "Interviews Today," and "Average Match Score" using Server Components for instant loading.
* **AI-Ranked Table**: Use TanStack Table to build a sortable list.
  - **Feature**: Implement "Semantic Search" where recruiters type natural language queries (e.g., "React dev with Python experience") which are sent to your ChromaDB backend.
  - **UI**: Color-coded badges for **Match Relevance** (e.g., Green > 85%, Yellow 60-84%, Red < 60%).

**B. Candidate Pipeline (Visual Kanban)**

* **Drag-and-Drop**: Use **@dnd-kit/core** to move candidate cards between columns (e.g., "Screening" → "Technical Interview" → "Offer").
* **Optimistic UI**: Leverage React 19.2’s `useOptimistic` **hook** so the card moves instantly on the UI while the backend update (Server Action) processes in the background.

**C. Resume Parser UI (Side-by-Side Review)**

* **Split View**: Use a 60/40 split screen. Left side: The original PDF using a worker-based renderer like **react-pdf-viewer**. Right side: The parsed structured data (Skills, Experience, Education).
* **Verification Mode**: Highlight extracted text in the PDF when a recruiter clicks a parsed skill on the right, providing visual proof of the candidate's qualifications.


## 3. UI & Styling (Tailwind CSS 4.0)

* **Theme Configuration**: Utilize the new **CSS-first** `@theme` block in Tailwind 4.0 for your corporate branding colors.
* **View Transitions**: Use the **View Transitions API** (standard in Next.js 16) to animate the transition from the Dashboard list to a specific Candidate Profile MDN View Transitions.

## 4. Quality Assurance & Testing

**Unit Testing (Vitest)**:

* Target: Logic for **Match Score Calculation** and **Skill Extraction Mapping**.
* Setup: Use vitest with the @testing-library/react for component unit tests Vitest Docs.

**End-to-End Testing (Playwright)**:

* Critical Path: Automate the "Upload Resume → Parse → Verify in Pipeline" flow.
* Visual Regression: Use expect(page).toHaveScreenshot() to ensure the Resume Parser UI layout doesn't break across updates.

## 5. TypeScript Specifications

* **Global Types**: Define a strict Candidate interface:
```typescript
export type CandidateStatus = 'Applied' | 'Screening' | 'Interview' | 'Hired' | 'Rejected';

export interface Candidate {
  id: string;
  name: string;
  matchScore: number; // 0-100
  extractedSkills: string[];
  resumeUrl: string;
  currentStatus: CandidateStatus;
}
```
* Safe Server Actions: Use Zod to validate all incoming candidate data on the server side to prevent injection attacks or malformed resume data.

