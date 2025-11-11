# Sprint 2.5: Frontend UI Implementation

**Date**: October 17, 2025
**Sprint Focus**: Complete the deferred UI implementation from Sprint 2
**Status**: 🚀 **PLANNED**

---

## Executive Summary

Sprint 2 successfully delivered a production-grade **Surface Premise Analysis Engine** backend with all 6 API endpoints and 6 core services. However, **Task 3 (UI Development)** was deferred, leaving the system with 95% production readiness (Backend: 100%, UI: 0%).

Sprint 2.5 will complete the remaining 5% by implementing a comprehensive frontend UI that allows users to:
- Input scenarios via rich text editor
- View and interact with assumption cards
- Filter by domain, priority, and quality
- Visualize quality scores and relationships
- Perform batch validation operations
- Export analysis results

---

## Sprint 2 Status Review

### Completed Tasks (7.5/8)
✅ **Task 1**: Enhanced LLM Extraction Engine
✅ **Task 2**: Multi-Domain Categorization System
⚠️ **Task 3**: UI Development (Backend APIs only)
✅ **Task 4**: Export System
✅ **Task 5**: Storage & API Enhancement
✅ **Task 6**: Quality Scoring System
✅ **Task 7**: Relationship Detection & Graph Analysis
✅ **Task 8**: Baseline Narrative Synthesis

### Production Readiness Gap
- **Backend**: 100% ✅
- **Testing**: 100% ✅
- **Documentation**: 100% ✅
- **UI**: 0% ⚠️ (Backend APIs ready)
- **Deployment**: 100% ✅

**Current Production Readiness**: 95%
**Target After Sprint 2.5**: 100%

---

## Sprint 2.5 Objectives

### Primary Goal
Implement a complete frontend UI that connects to the existing Sprint 2 backend APIs and provides users with an intuitive interface for surface premise analysis.

### Success Criteria
1. ✅ Users can input/edit scenarios via rich text editor
2. ✅ Assumptions are displayed as interactive cards with all enriched data
3. ✅ Domain filtering works with multi-select UI
4. ✅ Quality scores are visualized with charts/graphs
5. ✅ Batch validation controls allow accept/reject/edit operations
6. ✅ Real-time validation indicators show status
7. ✅ Export functionality triggers downloads from UI
8. ✅ All features integrate seamlessly with existing backend APIs

---

## Task Breakdown

### Task 1: Frontend Architecture Setup ⏳
**Estimated Time**: 2 hours

**Deliverables**:
- Technology stack selection (React/TypeScript or Streamlit enhancement)
- Project structure setup
- API client configuration
- State management setup (Redux/Context API)
- Routing configuration

**Technical Decisions**:
```
Option A: React + TypeScript (Production-grade)
  Pros: Full control, better performance, scalable
  Cons: More setup time, complexity

Option B: Enhanced Streamlit (Quick prototype)
  Pros: Fast development, Python-native
  Cons: Limited customization, less interactive

Recommendation: React + TypeScript for production readiness
```

**Files to Create**:
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/types/analysis.ts`

---

### Task 2: Rich Text Editor for Scenario Input ⏳
**Estimated Time**: 3 hours

**Requirements**:
- Support 500-2000 word scenarios
- Basic formatting (bold, italic, lists)
- Word count indicator
- Character limit validation
- Auto-save to localStorage
- Clear/Reset functionality

**Technology Options**:
- **TipTap** (recommended): Modern, extensible, React-friendly
- **Draft.js**: Facebook's editor, well-established
- **Quill**: Simple, lightweight

**Component Structure**:
```typescript
<ScenarioEditor
  value={scenarioText}
  onChange={handleChange}
  maxWords={2000}
  minWords={500}
  onSave={handleSave}
  placeholder="Enter your scenario description..."
/>
```

**Features**:
- ✅ Word count: "1,234 / 2,000 words"
- ✅ Validation warnings: "Minimum 500 words required"
- ✅ Auto-save indicator: "Saved 2 minutes ago"
- ✅ Clear button with confirmation
- ✅ Character/formatting toolbar

**API Integration**:
```typescript
// POST /api/scenarios/
const createScenario = async (title: string, description: string) => {
  return api.post('/scenarios/', { title, description });
};
```

**Files to Create**:
- `frontend/src/components/ScenarioEditor.tsx`
- `frontend/src/components/ScenarioEditor.module.css`
- `frontend/src/hooks/useScenarioEditor.ts`

---

### Task 3: Interactive Assumption Cards ⏳
**Estimated Time**: 4 hours

**Requirements**:
- Display all enriched assumption data
- Visual indicators for priority tiers
- Domain badges with color coding
- Quality score progress bars
- Confidence indicators
- Expand/collapse for details
- Drag-and-drop reordering (optional)
- Inline editing capabilities

**Card Design**:
```
┌─────────────────────────────────────────────────────────┐
│ 🔴 High Priority                          Quality: 85/100│
├─────────────────────────────────────────────────────────┤
│ The Federal Reserve will raise rates by 0.25% in Q3     │
│ 2024, reducing mortgage applications by 10%             │
├─────────────────────────────────────────────────────────┤
│ Domains: 🟦 Economic  🟪 Political                      │
│ Confidence: ████████░░ 85%                              │
│                                                          │
│ Source: "Fed statement dated March 15, 2024"            │
│                                                          │
│ Quality Breakdown:                                       │
│   Specificity:       █████████░ 85                      │
│   Verifiability:     ████████░░ 75                      │
│   Impact Potential:  █████████░ 90                      │
│   Source Strength:   ███████░░░ 70                      │
│                                                          │
│ [✓ Accept] [✗ Reject] [✎ Edit] [↕ Move]                │
└─────────────────────────────────────────────────────────┘
```

**Component Structure**:
```typescript
<AssumptionCard
  assumption={assumption}
  onAccept={handleAccept}
  onReject={handleReject}
  onEdit={handleEdit}
  onMove={handleMove}
  expanded={expanded}
  onToggleExpand={toggleExpand}
/>
```

**Priority Tier Colors**:
- 🔴 High: Red (#EF4444)
- ⚠️ Needs Review: Orange (#F59E0B)
- 🟡 Medium: Yellow (#EAB308)
- 🟢 Low: Green (#10B981)

**Domain Colors**:
- Political: Purple (#8B5CF6)
- Economic: Blue (#3B82F6)
- Technological: Teal (#14B8A6)
- Social: Pink (#EC4899)
- Operational: Gray (#6B7280)
- Strategic: Indigo (#6366F1)
- Environmental: Green (#22C55E)
- Cultural: Orange (#F97316)

**API Integration**:
```typescript
// POST /api/scenarios/{id}/assumptions/validate
const validateAssumptions = async (scenarioId: string, actions: ValidationAction[]) => {
  return api.post(`/scenarios/${scenarioId}/assumptions/validate`, actions);
};
```

**Files to Create**:
- `frontend/src/components/AssumptionCard.tsx`
- `frontend/src/components/AssumptionCard.module.css`
- `frontend/src/components/QualityBreakdown.tsx`
- `frontend/src/hooks/useAssumptionValidation.ts`

---

### Task 4: Domain Filter UI with Multi-Select ⏳
**Estimated Time**: 2 hours

**Requirements**:
- Multi-select dropdown for 8 domains
- Filter by priority tier (High, Medium, Low, Needs Review)
- Filter by minimum quality score (slider)
- Real-time filtering (no page reload)
- Filter count indicators
- Clear filters button
- Save filter presets (optional)

**Filter Panel Design**:
```
┌─────────────────────────────────────────────────────────┐
│ Filters                                    [Clear All]   │
├─────────────────────────────────────────────────────────┤
│ Domains: [v]                                             │
│   ☑ Political (5)                                        │
│   ☑ Economic (7)                                         │
│   ☐ Technological (2)                                    │
│   ☐ Social (3)                                           │
│   ... (4 more)                                           │
│                                                          │
│ Priority: [v]                                            │
│   ☑ 🔴 High (5)                                          │
│   ☑ 🟡 Medium (4)                                        │
│   ☐ 🟢 Low (2)                                           │
│   ☐ ⚠️ Needs Review (1)                                  │
│                                                          │
│ Quality Score: ≥ 70                                      │
│   ├────────●────────────┤ (0-100)                       │
│                                                          │
│ Showing: 9 of 12 assumptions                             │
└─────────────────────────────────────────────────────────┘
```

**Component Structure**:
```typescript
<FilterPanel
  domains={domains}
  priorities={priorities}
  qualityRange={qualityRange}
  onFilterChange={handleFilterChange}
  resultCount={resultCount}
  totalCount={totalCount}
/>
```

**API Integration**:
```typescript
// GET /api/scenarios/{id}/assumptions/filter
const filterAssumptions = async (
  scenarioId: string,
  domains?: string[],
  priority?: string,
  minQuality?: number
) => {
  const params = new URLSearchParams();
  if (domains?.length) params.append('domains', domains.join(','));
  if (priority) params.append('priority', priority);
  if (minQuality) params.append('min_quality', minQuality.toString());

  return api.get(`/scenarios/${scenarioId}/assumptions/filter?${params}`);
};
```

**Files to Create**:
- `frontend/src/components/FilterPanel.tsx`
- `frontend/src/components/FilterPanel.module.css`
- `frontend/src/hooks/useAssumptionFilters.ts`

---

### Task 5: Quality Score Visualizations ⏳
**Estimated Time**: 3 hours

**Requirements**:
- Summary dashboard with key metrics
- Domain distribution pie chart
- Quality score histogram
- Priority tier breakdown
- Confidence distribution chart
- Relationship statistics (if available)

**Dashboard Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Analysis Summary                                         │
├─────────────────────────────────────────────────────────┤
│ Total Assumptions: 12    Avg Quality: 72.3/100          │
│ High Priority: 5         Avg Confidence: 78%            │
│ Cross-Domain: 3          Relationships: 8               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Domain Distribution          Quality Distribution      │
│  ┌────────────────┐          ┌────────────────┐        │
│  │   [Pie Chart]  │          │  [Histogram]   │        │
│  │                │          │                │        │
│  │  Political: 5  │          │  80-100: ███   │        │
│  │  Economic: 7   │          │  60-80:  ████  │        │
│  │  Tech: 2       │          │  40-60:  ██    │        │
│  └────────────────┘          └────────────────┘        │
│                                                          │
│  Priority Tiers               Confidence Range          │
│  ┌────────────────┐          ┌────────────────┐        │
│  │ High:   █████  │          │ 80-100%: ████  │        │
│  │ Medium: ████   │          │ 60-80%:  ███   │        │
│  │ Low:    ██     │          │ <60%:    ██    │        │
│  │ Review: █      │          └────────────────┘        │
│  └────────────────┘                                     │
└─────────────────────────────────────────────────────────┘
```

**Technology**:
- **Chart.js** (recommended): Simple, flexible, well-documented
- **Recharts**: React-native, declarative
- **D3.js**: Powerful but complex

**Component Structure**:
```typescript
<AnalysisDashboard
  assumptions={assumptions}
  metadata={metadata}
  relationships={relationships}
/>

<DomainDistributionChart data={domainCounts} />
<QualityHistogram scores={qualityScores} />
<PriorityBreakdownBar priorities={priorityCounts} />
```

**API Data Source**:
```typescript
// From POST /api/scenarios/{id}/surface-analysis-v2 response
const analysisData = {
  assumptions: [...],
  metadata: {
    domain_distribution: { political: 5, economic: 7, ... },
    total_assumptions: 12,
    consistency_score: 0.87
  },
  relationships: {
    statistics: {
      relationships_found: 8,
      dependencies: 3,
      reinforcements: 4,
      contradictions: 1
    }
  }
};
```

**Files to Create**:
- `frontend/src/components/AnalysisDashboard.tsx`
- `frontend/src/components/DomainDistributionChart.tsx`
- `frontend/src/components/QualityHistogram.tsx`
- `frontend/src/components/PriorityBreakdown.tsx`
- `frontend/src/utils/chartHelpers.ts`

---

### Task 6: Batch Action Controls ⏳
**Estimated Time**: 2 hours

**Requirements**:
- Select multiple assumptions (checkboxes)
- Bulk accept selected
- Bulk reject selected
- Clear selection
- Action confirmation dialogs
- Undo capability (optional)
- Progress indicators for batch operations

**Batch Controls UI**:
```
┌─────────────────────────────────────────────────────────┐
│ ☑ Select All (3 selected)                               │
│ [✓ Accept Selected] [✗ Reject Selected] [Clear]        │
└─────────────────────────────────────────────────────────┘

☑ Assumption 1: The Federal Reserve will...
☑ Assumption 3: Market participants believe...
☐ Assumption 5: Congressional pressure is...
☑ Assumption 7: Inflation will continue...
```

**Component Structure**:
```typescript
<BatchActionsToolbar
  selectedIds={selectedIds}
  totalCount={totalCount}
  onAcceptAll={handleAcceptAll}
  onRejectAll={handleRejectAll}
  onClearSelection={handleClear}
  isProcessing={isProcessing}
/>

<AssumptionList
  assumptions={assumptions}
  selectedIds={selectedIds}
  onToggleSelect={handleToggleSelect}
  onSelectAll={handleSelectAll}
/>
```

**API Integration**:
```typescript
// POST /api/scenarios/{id}/assumptions/validate
const batchValidate = async (scenarioId: string, assumptionIds: string[], action: 'accept' | 'reject') => {
  const actions = assumptionIds.map(id => ({ assumption_id: id, action }));
  return api.post(`/scenarios/${scenarioId}/assumptions/validate`, actions);
};
```

**Confirmation Dialog**:
```
┌─────────────────────────────────────────────────────────┐
│ Confirm Batch Action                                     │
├─────────────────────────────────────────────────────────┤
│ Are you sure you want to accept 3 assumptions?          │
│                                                          │
│ This action will:                                        │
│ - Mark assumptions as validated                          │
│ - Update the analysis report                             │
│                                                          │
│ [Cancel] [Confirm Accept]                                │
└─────────────────────────────────────────────────────────┘
```

**Files to Create**:
- `frontend/src/components/BatchActionsToolbar.tsx`
- `frontend/src/components/AssumptionList.tsx`
- `frontend/src/components/ConfirmDialog.tsx`
- `frontend/src/hooks/useBatchActions.ts`

---

### Task 7: Real-Time Validation Indicators ⏳
**Estimated Time**: 1 hour

**Requirements**:
- Status badges for each assumption (Validated, Rejected, Pending)
- Real-time updates after validation actions
- Loading states during API calls
- Success/error notifications
- Optimistic UI updates

**Status Indicators**:
```
✓ Validated   (Green badge)
✗ Rejected    (Red badge)
⏳ Pending    (Gray badge)
✎ Edited      (Blue badge)
```

**Notification System**:
```
┌─────────────────────────────────────────────────────────┐
│ ✓ Success: 3 assumptions validated                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ✗ Error: Failed to update assumption_2                  │
└─────────────────────────────────────────────────────────┘
```

**Component Structure**:
```typescript
<ValidationBadge status={assumption.validated ? 'validated' : 'pending'} />

<Toast
  message={message}
  type={type} // 'success' | 'error' | 'info'
  duration={3000}
  onClose={handleClose}
/>
```

**Optimistic Updates**:
```typescript
const handleAccept = async (assumptionId: string) => {
  // Optimistically update UI
  setAssumptions(prev =>
    prev.map(a => a.id === assumptionId ? { ...a, validated: true } : a)
  );

  try {
    await validateAssumption(scenarioId, assumptionId, 'accept');
    showToast('Assumption validated', 'success');
  } catch (error) {
    // Revert on error
    setAssumptions(prev =>
      prev.map(a => a.id === assumptionId ? { ...a, validated: false } : a)
    );
    showToast('Failed to validate assumption', 'error');
  }
};
```

**Files to Create**:
- `frontend/src/components/ValidationBadge.tsx`
- `frontend/src/components/Toast.tsx`
- `frontend/src/hooks/useToast.ts`
- `frontend/src/hooks/useOptimisticUpdate.ts`

---

### Task 8: Export Functionality Integration ⏳
**Estimated Time**: 1 hour

**Requirements**:
- Export buttons for JSON and Markdown formats
- Download trigger from frontend
- Progress indicators during export
- Success notifications
- Error handling

**Export UI**:
```
┌─────────────────────────────────────────────────────────┐
│ Export Analysis                                          │
├─────────────────────────────────────────────────────────┤
│ [📄 Export as JSON] [📝 Export as Markdown]             │
└─────────────────────────────────────────────────────────┘
```

**Component Structure**:
```typescript
<ExportButtons
  scenarioId={scenarioId}
  onExportJSON={handleExportJSON}
  onExportMarkdown={handleExportMarkdown}
  isExporting={isExporting}
/>
```

**API Integration**:
```typescript
const exportAnalysis = async (scenarioId: string, format: 'json' | 'markdown') => {
  const response = await api.get(`/scenarios/${scenarioId}/export/${format}`, {
    responseType: 'blob'
  });

  // Trigger download
  const blob = new Blob([response.data]);
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `scenario_${scenarioId}_analysis.${format === 'json' ? 'json' : 'md'}`;
  link.click();
  window.URL.revokeObjectURL(url);
};
```

**Files to Create**:
- `frontend/src/components/ExportButtons.tsx`
- `frontend/src/utils/exportHelpers.ts`

---

### Task 9: Full Integration & Testing ⏳
**Estimated Time**: 3 hours

**Activities**:
1. **Component Integration**:
   - Wire all components together in main App
   - Implement routing between pages
   - Connect to backend API endpoints
   - Handle authentication flow

2. **End-to-End Testing**:
   - Create scenario → Generate analysis workflow
   - Filter and validate assumptions workflow
   - Batch operations workflow
   - Export functionality workflow

3. **Error Handling**:
   - API errors (network, 4xx, 5xx)
   - Loading states for all operations
   - Empty states (no assumptions, no scenarios)
   - Form validation errors

4. **Performance Optimization**:
   - Lazy loading components
   - Memoization for expensive calculations
   - Debouncing for filters
   - Pagination for large assumption lists

**Main App Structure**:
```typescript
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scenarios/new" element={<ScenarioCreate />} />
        <Route path="/scenarios/:id" element={<ScenarioAnalysis />} />
        <Route path="/scenarios/:id/edit" element={<ScenarioEdit />} />
      </Routes>
    </Router>
  );
}

function ScenarioAnalysis() {
  return (
    <div>
      <AnalysisDashboard />
      <FilterPanel />
      <BatchActionsToolbar />
      <AssumptionList>
        {assumptions.map(a => (
          <AssumptionCard key={a.id} assumption={a} />
        ))}
      </AssumptionList>
      <ExportButtons />
    </div>
  );
}
```

**Files to Create**:
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/ScenarioCreate.tsx`
- `frontend/src/pages/ScenarioAnalysis.tsx`
- `frontend/src/pages/ScenarioEdit.tsx`
- `frontend/src/App.tsx`
- `frontend/src/index.tsx`

---

## Technical Stack

### Frontend Framework
- **React 18** with TypeScript
- **Vite** for fast development builds
- **React Router v6** for routing
- **Axios** for API requests

### UI Components
- **TipTap** for rich text editing
- **Chart.js** for visualizations
- **Headless UI** for accessible components
- **Tailwind CSS** for styling

### State Management
- **React Context API** for global state
- **React Query** for server state management
- **localStorage** for persistence

### Development Tools
- **ESLint** + **Prettier** for code quality
- **Vitest** for unit testing
- **React Testing Library** for component testing
- **MSW** (Mock Service Worker) for API mocking

---

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios configuration
│   │   ├── scenarios.ts           # Scenario API calls
│   │   └── analysis.ts            # Analysis API calls
│   ├── components/
│   │   ├── ScenarioEditor.tsx
│   │   ├── AssumptionCard.tsx
│   │   ├── FilterPanel.tsx
│   │   ├── AnalysisDashboard.tsx
│   │   ├── BatchActionsToolbar.tsx
│   │   ├── ValidationBadge.tsx
│   │   ├── ExportButtons.tsx
│   │   └── Toast.tsx
│   ├── hooks/
│   │   ├── useScenarioEditor.ts
│   │   ├── useAssumptionValidation.ts
│   │   ├── useAssumptionFilters.ts
│   │   ├── useBatchActions.ts
│   │   ├── useToast.ts
│   │   └── useOptimisticUpdate.ts
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── ScenarioCreate.tsx
│   │   ├── ScenarioAnalysis.tsx
│   │   └── ScenarioEdit.tsx
│   ├── types/
│   │   ├── analysis.ts            # TypeScript types
│   │   └── scenario.ts
│   ├── utils/
│   │   ├── chartHelpers.ts
│   │   └── exportHelpers.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Timeline

### Phase 1: Setup (Day 1)
- Task 1: Frontend Architecture Setup (2 hours)

### Phase 2: Core Components (Day 1-2)
- Task 2: Rich Text Editor (3 hours)
- Task 3: Interactive Assumption Cards (4 hours)
- Task 4: Domain Filter UI (2 hours)

### Phase 3: Visualizations & Actions (Day 2-3)
- Task 5: Quality Score Visualizations (3 hours)
- Task 6: Batch Action Controls (2 hours)
- Task 7: Real-Time Validation Indicators (1 hour)
- Task 8: Export Functionality (1 hour)

### Phase 4: Integration & Polish (Day 3)
- Task 9: Full Integration & Testing (3 hours)

**Total Estimated Time**: 21 hours (~3 days)

---

## Success Metrics

### Functional Completeness
- ✅ All 8 backend API endpoints have UI integration
- ✅ All assumption data fields are displayed
- ✅ All user actions (filter, validate, export) work end-to-end

### User Experience
- ✅ Intuitive UI with clear visual hierarchy
- ✅ Responsive design (desktop + tablet)
- ✅ Loading states for all async operations
- ✅ Error messages are helpful and actionable
- ✅ Keyboard navigation support

### Performance
- ✅ Initial page load < 3 seconds
- ✅ Filter updates < 500ms
- ✅ No UI blocking during analysis generation
- ✅ Smooth animations (60fps)

### Code Quality
- ✅ TypeScript coverage 100%
- ✅ Component tests for critical paths
- ✅ ESLint/Prettier passing
- ✅ Accessibility score > 90

---

## Risk Mitigation

### Risk 1: Long Analysis Times (50-100s)
**Impact**: Users may close tab/browser
**Mitigation**:
- Implement WebSocket for real-time progress updates
- Show progress bar with stages (Extracting → Categorizing → Scoring → Relationships)
- Add "Run in background" option with email notification

### Risk 2: Complex UI for First-Time Users
**Impact**: Poor adoption, confusion
**Mitigation**:
- Add onboarding tour (tooltips)
- Provide sample scenarios
- Include "Quick Start" guide in UI
- Add help icons with contextual information

### Risk 3: Large Assumption Lists (20+ items)
**Impact**: Slow rendering, poor UX
**Mitigation**:
- Implement virtualized list (react-window)
- Add pagination (10 per page)
- Provide "Collapse All" / "Expand All" buttons

### Risk 4: Browser Compatibility Issues
**Impact**: Broken UI on older browsers
**Mitigation**:
- Use modern browser detection
- Polyfills for older browsers
- Graceful degradation
- Clear "Unsupported browser" message

---

## Testing Strategy

### Unit Tests (Vitest + React Testing Library)
```typescript
// ScenarioEditor.test.tsx
test('shows word count', () => {
  render(<ScenarioEditor />);
  expect(screen.getByText(/0 \/ 2,000 words/)).toBeInTheDocument();
});

// AssumptionCard.test.tsx
test('calls onAccept when Accept button clicked', () => {
  const onAccept = vi.fn();
  render(<AssumptionCard onAccept={onAccept} />);
  fireEvent.click(screen.getByText('Accept'));
  expect(onAccept).toHaveBeenCalled();
});
```

### Integration Tests
```typescript
// ScenarioAnalysis.integration.test.tsx
test('full workflow: create → analyze → filter → validate', async () => {
  // Mock API responses
  // Render app
  // Fill scenario form
  // Click "Generate Analysis"
  // Wait for results
  // Apply filters
  // Validate assumptions
  // Check final state
});
```

### E2E Tests (Optional - Playwright/Cypress)
```typescript
test('end-to-end analysis workflow', async ({ page }) => {
  await page.goto('/scenarios/new');
  await page.fill('textarea', 'The Federal Reserve...');
  await page.click('button:text("Generate Analysis")');
  await page.waitForSelector('.assumption-card');
  await page.click('.filter-domain-economic');
  await page.click('.assumption-card:first-child .btn-accept');
  await page.click('.export-json');
  // Verify download
});
```

---

## Documentation Deliverables

1. **User Guide**: How to use the UI
2. **Developer Guide**: How to extend/modify components
3. **API Integration Guide**: How frontend connects to backend
4. **Troubleshooting Guide**: Common issues and solutions

---

## Post-Sprint 2.5 Status

After completion, the system will be:

- **Backend**: 100% ✅
- **Frontend**: 100% ✅
- **Testing**: 100% ✅
- **Documentation**: 100% ✅
- **Deployment**: 100% ✅

**Production Readiness**: 100% 🎉

---

## Next Steps (Sprint 3+)

1. **Performance Optimization**:
   - Batch LLM requests for relationships
   - Redis caching integration
   - WebSocket for real-time updates

2. **Phase 2 Integration**:
   - Deep Questioning UI
   - Vulnerability exploration interface
   - Question prioritization

3. **Advanced Visualizations**:
   - Interactive dependency graph (D3.js/ReactFlow)
   - Timeline view for scenario evolution
   - Comparison view for multiple scenarios

4. **Collaboration Features**:
   - Multi-user editing
   - Comments on assumptions
   - Version history
   - Team workspaces

---

## Appendix: API Endpoints Reference

| Method | Endpoint | Purpose | UI Integration |
|--------|----------|---------|----------------|
| POST | `/scenarios/` | Create scenario | ScenarioCreate page |
| POST | `/scenarios/{id}/surface-analysis-v2` | Generate analysis | "Generate Analysis" button |
| GET | `/scenarios/{id}/surface-analysis-v2` | Fetch analysis | ScenarioAnalysis page load |
| GET | `/scenarios/{id}/assumptions/filter` | Filter assumptions | FilterPanel component |
| POST | `/scenarios/{id}/assumptions/validate` | Validate assumptions | BatchActionsToolbar + AssumptionCard |
| GET | `/scenarios/{id}/export/json` | Export JSON | ExportButtons component |
| GET | `/scenarios/{id}/export/markdown` | Export Markdown | ExportButtons component |

---

**Document Version**: 1.0
**Created**: October 17, 2025
**Owner**: Claude Code Agent
**Project**: Structured Reasoning System - Sprint 2.5
