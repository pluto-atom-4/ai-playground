## Plan: Reorganize ats-frontend Per High-Level Specification

The high-level specification requires building three core features (Dashboard, Pipeline Kanban, Resume Parser), plus testing and type safety. This plan reorganizes `ats-frontend` into a scalable structure with proper separation of concerns, installs required dependencies, and scaffolds directories and files to support these features.

### Steps

1. **Create comprehensive directory structure** – Add `components/` (ui, features), `lib/` (utilities, services), `app/api/` (route handlers), `types/` (global types), `hooks/` (custom hooks), `playwright/` (e2e tests), and `styles/` (CSS modules) under `src/`.

2. **Define global types and interfaces** – Create `src/types/candidate.ts` with strict `Candidate` interface and `CandidateStatus` enum per TypeScript spec; add `src/types/index.ts` as barrel export.

3. **Install essential npm packages** – Add TanStack Table (for AI-Ranked Table), @dnd-kit (for drag-and-drop Kanban), react-pdf-viewer (for PDF resume display), Zod (already present), and testing libraries (Vitest, Playwright, @testing-library/react).

4. **Scaffold feature components** – Create component files: Dashboard metric tiles, AI-Ranked Table, Pipeline Kanban board with optimistic UI, Resume Parser split-view, and Candidate Profile card.

5. **Create utility and service layers** – Add helper functions for match score calculation, skill extraction mapping, server actions for candidate updates, and API service layer for backend communication.

6. **Set up custom hooks** – Build hooks like `useOptimisticStatus()` (React 19.2), `useMatchScoreCalculation()`, `useCandidateFilter()`, and `usePDFViewer()` for component reusability.

7. **Add CSS modules and Tailwind theme** – Create modular `.module.css` files for complex layouts (Resume Parser split-view, Kanban); configure Tailwind 4.0 `@theme` block in `tailwind.config.ts` for corporate branding.

8. **Create test scaffolding** – Set up `vitest.config.ts`, Playwright configuration, and example test files for Match Score Calculation and critical Resume Upload → Parse → Pipeline flow.

9. **Add Next.js route handlers** – Create `src/app/api/` endpoints (e.g., `/api/candidates`, `/api/parse-resume`) with Zod validation and Server Action wrappers.

10. **Update implementation-planning.md** – Document all structural changes, dependency additions, and a phased implementation roadmap in the current file.

---

## Testing Strategy

### Unit Testing (Vitest)

**Framework**: Vitest with @testing-library/react for component and logic testing.

**Setup Requirements**:
- Install: `pnpm add --save-dev vitest @testing-library/react @testing-library/dom jsdom`
- Create `vitest.config.ts` with Next.js compatibility
- Configure test environment: `jsdom` for DOM testing
- Add to `package.json` scripts: `"test": "vitest"`, `"test:ui": "vitest --ui"`

**Test Targets**:
1. **Match Score Calculation** (`tests/unit/match-score.test.ts`)
   - Test TF-IDF ranking algorithm
   - Test semantic similarity scoring (0-100 range)
   - Test edge cases (empty skills, null candidates)
   - Test color badge classification logic

2. **Skill Extraction Mapping** (`tests/unit/skill-extraction.test.ts`)
   - Mock parser output and validate skill mapping
   - Test skill normalization (case-insensitive, synonym handling)
   - Verify badge color classification (Green > 85%, Yellow 60-84%, Red < 60%)
   - Test extraction from structured data

3. **Component Unit Tests**
   - `tests/unit/components/MetricTile.test.tsx`: Props rendering, number formatting
   - `tests/unit/components/CandidateCard.test.tsx`: Status updates with optimistic UI
   - `tests/unit/hooks/useOptimisticStatus.test.ts`: Hook behavior with React 19.2

**Coverage Target**: >80% for business logic and components.

### End-to-End Testing (Playwright)

**Framework**: Playwright for critical user flows.

**Setup Requirements**:
- Install: `pnpm add --save-dev @playwright/test`
- Create `playwright.config.ts` pointing to `http://localhost:3000`
- Create `tests/e2e/` directory with Playwright test files
- Add to `package.json` scripts: `"test:e2e": "playwright test"`, `"test:e2e:ui": "playwright test --ui"`

**Critical Paths** (E2E Tests):
1. **Upload Resume → Parse → Verify Pipeline** (`tests/e2e/resume-upload-to-pipeline.spec.ts`)
   - Steps: Upload PDF → Verify parsed data in split-view → Move to Pipeline
   - Assertions: PDF rendered, skills extracted, status updated
   - Expected duration: < 5 seconds per upload

2. **Dashboard Metrics → Filter → AI Ranking** (`tests/e2e/dashboard-ranking.spec.ts`)
   - Steps: Load Dashboard → Enter semantic query → Verify filtered + ranked results
   - Assertions: Metric tiles load, table sorts by match score, results <= 100
   - Expected duration: Page load < 2 seconds

3. **Kanban Drag-and-Drop with Optimistic UI** (`tests/e2e/kanban-drag-drop.spec.ts`)
   - Steps: Drag candidate card → Verify instant UI update → Verify backend persists
   - Assertions: Card moves immediately (optimistic), backend request completes, no duplicates
   - Expected duration: Drag operation completes in < 300ms

4. **Visual Regression Testing** (`tests/e2e/resume-parser-visual.spec.ts`)
   - Use `expect(page).toHaveScreenshot()` for Resume Parser layout
   - Ensures 60/40 split-view layout consistency across updates
   - Reference screenshots stored in `tests/e2e/screenshots/`

**Run Tests**:
```bash
# Unit tests
pnpm test

# Unit tests with UI
pnpm test:ui

# E2E tests (requires dev server running: pnpm dev)
pnpm test:e2e

# E2E tests with UI mode
pnpm test:e2e:ui

# Run all tests
pnpm test && pnpm test:e2e
```

---

## Styling Strategy: Tailwind + CSS Modules

**Approach**: Hybrid strategy for performance and maintainability.

### Tailwind CSS (Rapid Styling)

**Usage**:
- All utility styling for layout, spacing, colors, typography
- Dashboard metric tiles: `flex gap-4`, `rounded-lg`, `shadow-md`
- Tables, badges, responsive grids, buttons
- Color-coded match relevance badges

**Configuration** (`tailwind.config.ts`):
```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'match-green': '#10b981',    // > 85% match
        'match-yellow': '#f59e0b',   // 60-84% match
        'match-red': '#ef4444',      // < 60% match
        'brand-primary': '#3b82f6',  // Corporate branding
        'brand-secondary': '#1e40af',
      },
      spacing: {
        '60': '60%',
        '40': '40%',
      },
    },
  },
  plugins: [],
};

export default config;
```

### CSS Modules (Complex Layouts)

**Usage**: Scoped styles for complex, feature-specific layouts.

**Files to Create**:

1. **`src/styles/ResumeParserSplit.module.css`** – 60/40 split-view layout
   ```css
   .container {
     display: grid;
     grid-template-columns: 60% 40%;
     gap: 1rem;
     height: 100vh;
     background: #ffffff;
   }
   
   .pdfViewer {
     border-right: 2px solid #e5e7eb;
     overflow-y: auto;
     padding: 1rem;
   }
   
   .parsedData {
     overflow-y: auto;
     padding: 1rem;
     background: #f9fafb;
   }
   
   .highlightedText {
     background-color: #fef08a;
     cursor: pointer;
     padding: 0.125rem 0.25rem;
   }
   ```

2. **`src/styles/KanbanBoard.module.css`** – Drag-and-drop board layout
   ```css
   .board {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
     gap: 1.5rem;
     padding: 1.5rem;
     background: #f3f4f6;
     min-height: 100vh;
   }
   
   .column {
     background: #ffffff;
     border-radius: 0.5rem;
     padding: 1rem;
     min-height: 600px;
     box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
   }
   
   .columnHeader {
     font-weight: 600;
     font-size: 0.875rem;
     margin-bottom: 1rem;
     text-transform: uppercase;
     color: #374151;
   }
   
   .cardWrapper {
     margin-bottom: 1rem;
     transition: opacity 200ms ease;
   }
   
   .cardWrapper.dragging {
     opacity: 0.5;
   }
   ```

3. **`src/styles/MetricDashboard.module.css`** – Dashboard grid layout
   ```css
   .container {
     padding: 1.5rem;
     background: #f9fafb;
     min-height: 100vh;
   }
   
   .metricsGrid {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
     gap: 1.5rem;
     margin-bottom: 2rem;
   }
   
   .tableContainer {
     background: #ffffff;
     border-radius: 0.5rem;
     box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
     overflow: hidden;
   }
   ```

**Import Pattern in Components**:
```tsx
import styles from '@/styles/ResumeParserSplit.module.css';

export function ResumeParser() {
  return (
    <div className={styles.container}>
      <div className={styles.pdfViewer}>...</div>
      <div className={styles.parsedData}>...</div>
    </div>
  );
}
```

---

## Caching Strategy for NLP Ranking Results

**Requirement**: Heavy NLP ranking results computed once and reused across recruiter sessions.

**Implementation**: Next.js `unstable_cache()` wrapper around ranking computation.

### Server Action with Cache (`src/lib/server-actions.ts`)

```typescript
import { unstable_cache } from 'next/cache';
import { getCandidateRankings } from '@/services/backend';

// Cache rankings for 1 hour (3600 seconds)
const getCachedRankings = unstable_cache(
  async (jobDescriptionId: string) => {
    return await getCandidateRankings(jobDescriptionId);
  },
  ['candidate-rankings'],      // Cache key
  { revalidate: 3600 }         // Revalidate every 1 hour
);

export async function fetchRankingsWithCache(jobDescriptionId: string) {
  return getCachedRankings(jobDescriptionId);
}

// Manual cache invalidation on candidate updates
export async function invalidateRankingCache(jobDescriptionId: string) {
  // Next.js 16+ cache invalidation
  const { revalidateTag } = await import('next/cache');
  revalidateTag(`candidate-rankings-${jobDescriptionId}`);
}
```

**Cache Invalidation Strategy**:
- On candidate status update: Call `invalidateRankingCache(jobId)` in Server Action
- On new resume upload: Use `revalidatePath('/dashboard')`
- On semantic search: Cache search results with shorter TTL (300 seconds)
- Manual invalidation: Admin dashboard cache clear button (future feature)

**Monitoring Cache Performance**:
- Add performance logging to track cache hits vs. misses
- Monitor in Next.js Analytics dashboard
- Measure ranking retrieval time: Target < 500ms cached, < 3s uncached
- Adjust revalidation window (3600s baseline) based on data freshness needs

---

## Backend Integration (FastAPI)

**Assumed FastAPI Endpoints** (coordinated with ats-backend team):

### 1. **Parse Resume** (`POST /api/parse-resume`)

**Request**: `FormData` with PDF file
```bash
Content-Type: multipart/form-data
Body: file=<binary PDF>
```

**Response Schema**: 
```json
{
  "id": "resume-123",
  "candidateName": "John Doe",
  "email": "john@example.com",
  "skills": ["Python", "React", "PostgreSQL"],
  "experience": [
    {
      "role": "Senior Software Engineer",
      "company": "Tech Corp",
      "years": 3
    }
  ],
  "education": [
    {
      "degree": "B.S. Computer Science",
      "institution": "University"
    }
  ],
  "extractedText": "Full resume text..."
}
```

**Frontend Integration** (`src/services/resume-api.ts`):
```typescript
export async function parseResumeFile(file: File): Promise<ParsedResume> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/api/parse-resume`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) throw new Error('Resume parse failed');
  return response.json();
}
```

### 2. **Semantic Search** (`POST /api/semantic-search`)

**Request**: 
```json
{
  "query": "React developer with Python experience",
  "jobDescriptionId": "job-456",
  "limit": 50
}
```

**Response Schema**:
```json
{
  "results": [
    {
      "candidateId": "cand-1",
      "candidateName": "John Doe",
      "matchScore": 92,
      "relevantSkills": ["React", "Python"],
      "matchedKeywords": {"react": 0.95, "python": 0.88}
    }
  ],
  "queryTime": "245ms"
}
```

**Frontend Integration** (`src/services/search-api.ts`):
```typescript
export async function semanticSearch(
  query: string,
  jobId: string,
  limit = 50
): Promise<SearchResult[]> {
  const response = await fetch(`${API_BASE}/api/semantic-search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, jobDescriptionId: jobId, limit }),
  });
  
  if (!response.ok) throw new Error('Search failed');
  const data = await response.json();
  return data.results;
}
```

### 3. **Candidates Endpoint** (`GET/POST/PATCH /api/candidates`)

**GET** `/api/candidates?status=Screening&jobId=job-456&page=1&limit=20`
- Returns paginated candidates filtered by status
- Query params: `status`, `jobId`, `page`, `limit`
- Response: `{ data: Candidate[], total: number, page: number }`

**POST** `/api/candidates`
- Create new candidate entry after resume parsing
- Request: `{ name, email, resumeUrl, extractedSkills, currentStatus }`

**PATCH** `/api/candidates/{id}/status`
- Update candidate status (triggered by Server Action)
- Request: `{ status: "Interview", notes: "Good technical fit" }`
- Response: Updated candidate object

**Frontend Integration** (`src/services/candidates-api.ts`):
```typescript
export async function getCandidates(
  status?: CandidateStatus,
  jobId?: string,
  page = 1,
  limit = 20
): Promise<CandidatesResponse> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (jobId) params.append('jobId', jobId);
  params.append('page', String(page));
  params.append('limit', String(limit));
  
  const response = await fetch(`${API_BASE}/api/candidates?${params}`);
  if (!response.ok) throw new Error('Fetch candidates failed');
  return response.json();
}

export async function updateCandidateStatus(
  candidateId: string,
  status: CandidateStatus,
  notes?: string
): Promise<Candidate> {
  const response = await fetch(`${API_BASE}/api/candidates/${candidateId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, notes }),
  });
  
  if (!response.ok) throw new Error('Update failed');
  return response.json();
}
```

### Zod Validation for API Responses

**File**: `src/lib/validators.ts`
```typescript
import { z } from 'zod';

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
});

export const ParsedResumeSchema = z.object({
  id: z.string(),
  candidateName: z.string(),
  skills: z.array(z.string()),
  experience: z.array(z.object({
    role: z.string(),
    company: z.string(),
    years: z.number(),
  })),
  education: z.array(z.object({
    degree: z.string(),
    institution: z.string(),
  })),
});

export const SearchResultSchema = z.object({
  candidateId: z.string(),
  candidateName: z.string(),
  matchScore: z.number().min(0).max(100),
  relevantSkills: z.array(z.string()),
});
```

**Environment Variables** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_CACHING=true
```

**Validation Checklist**:
- [ ] FastAPI backend routes match expected paths (`/api/parse-resume`, `/api/semantic-search`, `/api/candidates`)
- [ ] Response schemas match TypeScript interfaces in `src/types/`
- [ ] CORS enabled on FastAPI for `http://localhost:3000`
- [ ] Error handling for network failures (timeout: 30s, retry: 3x)
- [ ] Zod validation on all response payloads before use
- [ ] API rate limiting configured (target: 100 req/min per client)
- [ ] Logging/monitoring for API performance in dev console

---

## Directory Structure Summary

```
ats-frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx (Dashboard)
│   │   ├── candidate/
│   │   │   └── [id]/
│   │   │       └── page.tsx (Candidate Detail)
│   │   ├── pipeline/
│   │   │   └── page.tsx (Kanban Board)
│   │   └── api/
│   │       ├── candidates/
│   │       │   └── route.ts
│   │       └── parse-resume/
│   │           └── route.ts
│   ├── components/
│   │   ├── ui/
│   │   │   ├── MetricTile.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Button.tsx
│   │   │   └── Card.tsx
│   │   ├── features/
│   │   │   ├── Dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── AIRankedTable.tsx
│   │   │   │   ├── MetricDashboard.tsx
│   │   │   │   └── SearchBar.tsx
│   │   │   ├── Pipeline/
│   │   │   │   ├── KanbanBoard.tsx
│   │   │   │   ├── CandidateCard.tsx
│   │   │   │   └── Column.tsx
│   │   │   ├── ResumeParser/
│   │   │   │   ├── ResumeParser.tsx
│   │   │   │   ├── PDFViewer.tsx
│   │   │   │   ├── ParsedDataPanel.tsx
│   │   │   │   └── SkillHighlight.tsx
│   │   │   └── CandidateProfile/
│   │   │       └── CandidateProfile.tsx
│   │   └── layouts/
│   │       └── MainLayout.tsx
│   ├── hooks/
│   │   ├── useOptimisticStatus.ts
│   │   ├── useMatchScoreCalculation.ts
│   │   ├── useCandidateFilter.ts
│   │   ├── usePDFViewer.ts
│   │   └── useSemanticSearch.ts
│   ├── lib/
│   │   ├── match-score.ts
│   │   ├── skill-extraction.ts
│   │   ├── server-actions.ts
│   │   ├── validators.ts (Zod schemas)
│   │   └── constants.ts
│   ├── services/
│   │   ├── backend.ts (Base API utility)
│   │   ├── resume-api.ts
│   │   ├── search-api.ts
│   │   └── candidates-api.ts
│   ├── styles/
│   │   ├── ResumeParserSplit.module.css
│   │   ├── KanbanBoard.module.css
│   │   ├── MetricDashboard.module.css
│   │   └── globals.css
│   ├── types/
│   │   ├── candidate.ts
│   │   ├── api.ts
│   │   └── index.ts (barrel export)
│   └── globals.css
├── tests/
│   ├── unit/
│   │   ├── match-score.test.ts
│   │   ├── skill-extraction.test.ts
│   │   ├── components/
│   │   │   ├── MetricTile.test.tsx
│   │   │   ├── CandidateCard.test.tsx
│   │   │   └── AIRankedTable.test.tsx
│   │   └── hooks/
│   │       ├── useOptimisticStatus.test.ts
│   │       └── useMatchScoreCalculation.test.ts
│   └── e2e/
│       ├── resume-upload-to-pipeline.spec.ts
│       ├── dashboard-ranking.spec.ts
│       ├── kanban-drag-drop.spec.ts
│       ├── resume-parser-visual.spec.ts
│       └── screenshots/
│           ├── resume-parser-reference.png
│           └── dashboard-reference.png
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── postcss.config.mjs
├── vitest.config.ts
├── playwright.config.ts
├── eslint.config.mjs
└── .env.local
```

---

## Phased Implementation Roadmap

**Phase 1: Foundation** (Week 1)
- [ ] Create directory structure under `src/`
- [ ] Define types: `src/types/candidate.ts`, `src/types/api.ts`
- [ ] Install npm packages (pnpm add for prod, --save-dev for dev)
- [ ] Configure Vitest (`vitest.config.ts`) and Playwright (`playwright.config.ts`)
- [ ] Update `tailwind.config.ts` with custom colors and spacing
- [ ] Create `.env.local` with API endpoint

**Phase 2: Components & Styling** (Week 2)
- [ ] Build Dashboard layout with metric tiles (`MetricTile.tsx`, `MetricDashboard.tsx`)
- [ ] Build AI-Ranked Table with TanStack Table (`AIRankedTable.tsx`)
- [ ] Create CSS modules: `ResumeParserSplit.module.css`, `MetricDashboard.module.css`
- [ ] Build UI component library (Button, Badge, Card)
- [ ] Set up MainLayout wrapper

**Phase 3: Advanced Features** (Week 3)
- [ ] Implement Kanban board with @dnd-kit (`KanbanBoard.tsx`, `Column.tsx`)
- [ ] Add optimistic UI with React 19.2 `useOptimistic` hook (`useOptimisticStatus.ts`)
- [ ] Build Resume Parser split-view (`ResumeParser.tsx`, `PDFViewer.tsx`, `ParsedDataPanel.tsx`)
- [ ] Create CSS module: `KanbanBoard.module.css`
- [ ] Implement SkillHighlight verification mode

**Phase 4: Backend Integration & Caching** (Week 4)
- [ ] Implement service layer (`src/services/backend.ts`, `resume-api.ts`, `search-api.ts`, `candidates-api.ts`)
- [ ] Add Zod validators (`src/lib/validators.ts`)
- [ ] Create Server Actions with `unstable_cache()` (`src/lib/server-actions.ts`)
- [ ] Implement match score calculation logic (`src/lib/match-score.ts`)
- [ ] Implement skill extraction mapping (`src/lib/skill-extraction.ts`)
- [ ] Create custom hooks: `useMatchScoreCalculation.ts`, `useCandidateFilter.ts`, `useSemanticSearch.ts`, `usePDFViewer.ts`

**Phase 5: Testing & Polish** (Week 5)
- [ ] Write unit tests for match score and skill extraction (Vitest)
- [ ] Write component unit tests (MetricTile, CandidateCard, AIRankedTable)
- [ ] Write E2E tests for critical paths (Playwright)
- [ ] Visual regression testing for Resume Parser layout
- [ ] Performance optimization and code cleanup
- [ ] Documentation and README updates

---

## Dependency Checklist

**Production Dependencies** (UI, data, AI features):
```bash
pnpm add @tanstack/react-table @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities react-pdf-viewer
```

**Dev Dependencies** (Testing, type checking):
```bash
pnpm add --save-dev vitest @testing-library/react @testing-library/dom jsdom @playwright/test
```

**Full Install Command**:
```bash
pnpm add @tanstack/react-table @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities react-pdf-viewer && \
pnpm add --save-dev vitest @testing-library/react @testing-library/dom jsdom @playwright/test
```

**Verify Installation**:
```bash
pnpm list | grep -E "@tanstack|@dnd-kit|react-pdf-viewer|vitest|playwright"
```

**Update package.json Scripts**:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "type-check": "tsc --noEmit"
  }
}
```

---

## Next Steps

1. **Review this plan** with the team for alignment
2. **Install dependencies** using the checklist above
3. **Execute Phase 1** (Foundation) – create directories and configure tools
4. **Begin Phase 2** (Components) – build UI component library
5. **Iterate** through remaining phases with regular testing and validation
