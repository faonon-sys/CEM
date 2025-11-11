# Sprint 4.5 Plan: Scoring, Visualization & Integration

**Date**: October 13, 2025
**Status**: 🔴 **NOT STARTED**
**Dependencies**: Sprint 4 (Complete ✅)

---

## Executive Summary

Sprint 4.5 continues the Phase 3 implementation by adding advanced scoring algorithms, comprehensive frontend visualization, and full pipeline integration. This sprint transforms the backend foundation from Sprint 4 into a complete, user-facing system with sophisticated risk analysis capabilities.

### Scope Overview

| Component | Status | Estimated Effort |
|-----------|--------|------------------|
| **Scoring Engine** | 🔴 Not Started | 24-32 hours |
| **Frontend UI** | 🔴 Not Started | 88-112 hours |
| **Integration & Testing** | 🔴 Not Started | 40-48 hours |
| **Overall** | 🔴 Not Started | **152-192 hours (3-5 weeks)** |

---

## 🔴 Sprint 4.5 Tasks (5 Tasks)

### Task 4: Multi-Factor Severity & Probability Rating System

**Status**: Not Started
**Estimated Effort**: 24-32 hours
**Priority**: 🔴 High (blocks visualization accuracy)

#### Requirements

1. **Multi-Factor Scoring Algorithms:**
   - **Severity Components:**
     - Cascade depth (number of levels in consequence chain)
     - Impact breadth (number of affected domains/actors)
     - Deviation magnitude (how far from baseline scenario)
     - Irreversibility (difficulty of returning to baseline)
   - **Probability Components:**
     - Evidence strength (how well-supported by data)
     - Historical precedent (frequency of similar events)
     - Dependency requirements (complexity of preconditions)
     - Time horizon (urgency vs. long-term)

2. **Confidence Interval Calculation:**
   - Bootstrap resampling for uncertainty quantification
   - Monte Carlo simulation for probability distributions
   - 90% confidence intervals for all scores

3. **Human-in-the-Loop Calibration:**
   - Web interface for expert score adjustments
   - Learning from historical calibrations
   - Correlation validation with expert assessments (target: 70%+)

4. **Sensitivity Analysis:**
   - Identify which factors most influence scores
   - Scenario comparison with score perturbations
   - Robustness testing

#### Files to Create

- `backend/services/scoring_engine.py` (400-500 lines)
  - `class SeverityScorer`: Multi-factor severity calculation
  - `class ProbabilityScorer`: Multi-factor probability calculation
  - `class ConfidenceIntervalCalculator`: Bootstrap/Monte Carlo methods
  - `class SensitivityAnalyzer`: Factor importance analysis

- `backend/api/scoring.py` (200-300 lines)
  - `POST /api/scoring/calibrate`: Submit expert scores
  - `GET /api/scoring/sensitivity/{scenario_id}`: Get sensitivity analysis
  - `POST /api/scoring/batch`: Batch score scenarios

- `backend/services/sensitivity_analysis.py` (200-300 lines)
  - `class FactorPerturbation`: Perturb individual factors
  - `class ScoreVarianceAnalysis`: Measure impact of perturbations

#### Acceptance Criteria

- ✅ Severity scores use all 4 components with configurable weights
- ✅ Probability scores use all 4 components with configurable weights
- ✅ Confidence intervals calculated for all scenarios
- ✅ Calibration interface allows expert adjustments
- ✅ Correlation with expert scores ≥70%
- ✅ Sensitivity analysis identifies top 3 influential factors per scenario

---

### Task 5: D3.js Network Visualization

**Status**: Not Started
**Estimated Effort**: 32-40 hours
**Priority**: 🔴 High (highest user value)

#### Requirements

1. **Interactive Network Graph:**
   - **Node Types:**
     - Assumptions (Phase 1) - blue circles
     - Fragilities (Phase 2) - orange triangles
     - Breaches (Phase 3) - red squares
     - Counterfactuals (Phase 3) - purple diamonds
   - **Edge Types:**
     - Dependency links (solid lines)
     - Consequence chains (dashed lines)
     - Phase transitions (thick lines)

2. **Layout & Performance:**
   - Force-directed layout (D3.js or React Flow)
   - Canvas rendering for >100 nodes (fallback from SVG)
   - Web Workers for layout calculation
   - Performance target: <2s render time for 100 nodes

3. **Interactivity:**
   - Hover: Show node details in tooltip
   - Click: Open detail panel with full information
   - Drag: Reposition nodes (persist layout)
   - Zoom: Smooth zoom with limits (0.1x - 5x)
   - Filter: Show/hide node types, severity ranges
   - Search: Highlight nodes matching search query

4. **Detail Panels:**
   - Assumption: Name, description, confidence
   - Fragility: Description, contributing assumptions, severity
   - Breach: Trigger event, preconditions, plausibility
   - Counterfactual: Narrative, timeline, consequences, scores

#### Files to Create

- `frontend/components/NetworkGraph.tsx` (400-500 lines)
  - SVG-based graph for <100 nodes
  - Force simulation with collision detection
  - Interactive controls (zoom, pan, filter)

- `frontend/components/NetworkGraphCanvas.tsx` (300-400 lines)
  - Canvas-based graph for >100 nodes
  - Web Worker for layout calculation
  - Optimized rendering with RAF

- `frontend/hooks/useNetworkData.ts` (150-200 lines)
  - Fetch graph data from API
  - Transform to D3 format
  - Manage layout state

- `frontend/services/graph_layout.ts` (200-300 lines)
  - Custom force simulation parameters
  - Collision detection
  - Layout persistence (localStorage)

- `frontend/components/NodeDetailPanel.tsx` (200-300 lines)
  - Type-specific detail rendering
  - Edit/delete actions (admin)

#### Acceptance Criteria

- ✅ Renders 100+ node graphs in <2 seconds
- ✅ All node types visually distinguishable
- ✅ Hover, click, drag, zoom, filter all functional
- ✅ Detail panel shows complete node information
- ✅ Layout persists across sessions
- ✅ Smooth animations (60 FPS on modern hardware)

---

### Task 6: Heat Maps & Dashboard

**Status**: Not Started
**Estimated Effort**: 32-40 hours
**Priority**: 🟡 Medium

#### Requirements

1. **2D Heat Maps:**
   - **Axes × Domains Heat Map:**
     - X-axis: 6 strategic axes
     - Y-axis: Affected domains (military, economic, etc.)
     - Cell color: Severity (0-10 scale)
     - Cell count: Number of counterfactuals
   - **Axes × Time Heat Map:**
     - X-axis: 6 strategic axes
     - Y-axis: Time horizons (short/medium/long)
     - Cell color: Probability (0-1 scale)
   - **Domains × Severity Heat Map:**
     - X-axis: Affected domains
     - Y-axis: Severity ranges (0-3, 3-6, 6-10)
     - Cell color: Counterfactual count

2. **Interactive Drill-Down:**
   - Click cell → Filter counterfactuals list
   - Display matching scenarios in sidebar
   - Link to network graph (highlight nodes)

3. **Summary Statistics Panel:**
   - Total counterfactuals generated
   - Average severity by axis
   - Highest risk domain
   - Most likely time horizon
   - Portfolio counts

4. **Export Functionality:**
   - Export heat maps to PNG/PDF
   - Export summary statistics to CSV
   - Export full report to PDF

5. **Responsive Layout:**
   - Desktop: Side-by-side heat maps
   - Tablet: Stacked heat maps
   - Mobile: Swipeable carousel

#### Files to Create

- `frontend/components/HeatMap.tsx` (300-400 lines)
  - Generic heat map component
  - Configurable axes, color scales
  - Interactive click handlers

- `frontend/components/RiskDashboard.tsx` (400-500 lines)
  - Three heat maps (axes×domains, axes×time, domains×severity)
  - Summary statistics panel
  - Drill-down sidebar

- `frontend/services/heatmap_generator.ts` (200-300 lines)
  - Data aggregation for heat maps
  - Color scale calculation
  - Cell value computation

- `frontend/utils/export_utils.ts` (150-200 lines)
  - PNG export (html2canvas)
  - PDF export (jsPDF)
  - CSV export (Papa Parse)

#### Acceptance Criteria

- ✅ All 3 heat maps render correctly with accurate data
- ✅ Click cell → Filter counterfactuals (show matching scenarios)
- ✅ Summary statistics update based on filters
- ✅ Export to PNG, PDF, CSV functional
- ✅ Responsive layout works on desktop/tablet/mobile

---

### Task 7: Comparison & Selection Interface

**Status**: Not Started
**Estimated Effort**: 24-32 hours
**Priority**: 🟡 Medium

#### Requirements

1. **Side-by-Side Comparison:**
   - Compare 2-4 scenarios simultaneously
   - Show narrative, timeline, consequences, scores
   - Highlight differences in red/green
   - Export comparison to PDF

2. **Matrix View:**
   - All counterfactuals in sortable table
   - Columns: Axis, Severity, Probability, Domains, Timeline
   - Sort by any column (ascending/descending)
   - Filter by axis, domain, severity range, probability range
   - Pagination (20 per page)

3. **Portfolio Builder:**
   - Drag-and-drop scenarios into portfolios
   - Name and describe portfolios
   - Save portfolios to database
   - Load existing portfolios
   - Export portfolios to Phase 5

4. **Overlap Analysis:**
   - Identify common consequences across 3+ scenarios
   - Highlight systemic risks (appear in 50%+ scenarios)
   - Visualize consequence frequency bar chart

5. **Phase 5 Export:**
   - Export selected counterfactuals to Phase 5 format
   - Include full lineage (Phase 1 → Phase 2 → Phase 3)
   - JSON format with schema validation

#### Files to Create

- `frontend/components/ScenarioComparison.tsx` (300-400 lines)
  - Side-by-side comparison view (2-4 scenarios)
  - Diff highlighting
  - Export to PDF

- `frontend/components/ScenarioMatrix.tsx` (300-400 lines)
  - Sortable, filterable table
  - Pagination
  - Row selection for comparison

- `frontend/components/PortfolioBuilder.tsx` (400-500 lines)
  - Drag-and-drop interface (react-dnd)
  - Portfolio CRUD operations
  - Overlap analysis visualizations

- `backend/api/portfolios.py` (200-300 lines)
  - `POST /api/portfolios`: Create portfolio
  - `GET /api/portfolios`: List portfolios
  - `GET /api/portfolios/{id}`: Get portfolio details
  - `PUT /api/portfolios/{id}`: Update portfolio
  - `DELETE /api/portfolios/{id}`: Delete portfolio
  - `POST /api/portfolios/{id}/export`: Export to Phase 5

#### Acceptance Criteria

- ✅ Side-by-side comparison works for 2-4 scenarios
- ✅ Matrix view supports sorting, filtering, pagination
- ✅ Portfolio builder allows drag-and-drop scenario management
- ✅ Overlap analysis identifies common consequences
- ✅ Phase 5 export generates valid JSON

---

### Task 8: Phase 2-3 Pipeline & Testing

**Status**: Not Started
**Estimated Effort**: 40-48 hours
**Priority**: 🔴 High (critical for production readiness)

#### Requirements

1. **Automated Pipeline:**
   - **Phase 2 → Phase 3 Flow:**
     1. Detect Phase 2 completion event
     2. Fetch fragility analysis results
     3. Generate breach conditions (Task 2 engine)
     4. Generate counterfactuals (Task 3 engine)
     5. Score scenarios (Task 4 engine)
     6. Store in database
     7. Trigger frontend refresh
   - **Data Validation Checkpoints:**
     - Validate Phase 2 output schema
     - Validate breach conditions (structure, plausibility)
     - Validate counterfactuals (narrative length, timeline)
     - Validate scores (ranges, confidence intervals)
   - **Error Recovery:**
     - Retry failed LLM calls (3x with exponential backoff)
     - Fall back to template generation on persistent failures
     - Log all errors with context
     - Send alerts on critical failures

2. **API Endpoints:**
   - `POST /api/phase3/generate`: Trigger Phase 2 → Phase 3 pipeline
   - `GET /api/phase3/scenarios`: List all counterfactuals
   - `GET /api/phase3/scenarios/{id}`: Get scenario details
   - `GET /api/phase3/scenarios/{id}/graph`: Get consequence graph
   - `PUT /api/phase3/scenarios/{id}/score`: Update scores (calibration)
   - `DELETE /api/phase3/scenarios/{id}`: Delete scenario

3. **Integration Tests:**
   - 10+ end-to-end scenarios across diverse domains
   - Test with 5, 10, 20, 50 fragilities
   - Validate output quality (narrative coherence, score accuracy)
   - Performance benchmarks (time per scenario, throughput)

4. **Unit Tests:**
   - Test all services in isolation
   - Mock LLM responses for deterministic tests
   - Test error handling and fallbacks
   - Target: 90%+ code coverage

5. **CI/CD Integration:**
   - GitHub Actions workflow
   - Run tests on every PR
   - Deploy to staging on merge to main
   - Production deployment requires manual approval

#### Files to Create

- `backend/services/phase3_pipeline.py` (400-500 lines)
  - `class Phase3Pipeline`: Orchestrates full pipeline
  - `async def run_pipeline(phase2_output)`: Main entry point
  - Validation checkpoints, error recovery

- `backend/api/phase3_endpoints.py` (300-400 lines)
  - All Phase 3 API endpoints
  - Request/response validation (Pydantic)
  - Error handling and logging

- `tests/integration/test_phase2_to_phase3.py` (500-600 lines)
  - 10+ end-to-end scenarios
  - Performance benchmarks
  - Output quality validation

- `tests/unit/test_breach_engine.py` (300-400 lines)
  - Test breach generation
  - Test axis mapping
  - Test fallbacks and error handling

- `tests/unit/test_counterfactual_generator.py` (300-400 lines)
  - Test timeline generation
  - Test cascade tracing
  - Test narrative generation

- `tests/unit/test_scoring_engine.py` (300-400 lines)
  - Test severity calculation
  - Test probability calculation
  - Test confidence intervals

- `.github/workflows/ci.yml` (100-150 lines)
  - Run tests on PR
  - Deploy to staging
  - Production deployment gate

#### Acceptance Criteria

- ✅ Pipeline processes Phase 2 output automatically
- ✅ All validation checkpoints pass for test data
- ✅ Error recovery handles LLM failures gracefully
- ✅ 10+ integration tests pass
- ✅ Unit tests achieve 90%+ coverage
- ✅ CI/CD workflow deploys to staging successfully
- ✅ Performance: <2 minutes for 20 fragilities

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                Sprint 4.5 Target Architecture                     │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Phase 2       │  Fragility analysis output
│   Output        │  (existing from Sprint 3)
└────────┬────────┘
         │
         v
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (Sprint 4.5)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✅ Task 1-3: Foundation (Sprint 4 Complete)                    │
│  ├─ phase3_schema.py                                            │
│  ├─ axis_framework.py                                           │
│  ├─ breach_engine.py                                            │
│  └─ counterfactual_generator.py                                 │
│                                                                  │
│  🔴 Task 4: Scoring Engine (Sprint 4.5)                         │
│  └─ scoring_engine.py                                           │
│     ├─ Multi-factor severity/probability                        │
│     ├─ Confidence intervals                                     │
│     └─ Sensitivity analysis                                     │
│                                                                  │
│  🔴 Task 8: Pipeline & API (Sprint 4.5)                         │
│  ├─ phase3_pipeline.py (orchestration)                          │
│  ├─ phase3_endpoints.py (REST API)                              │
│  └─ Integration + unit tests (90%+ coverage)                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (Sprint 4.5)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔴 Task 5: D3.js Network Visualization                         │
│  ├─ NetworkGraph.tsx (SVG for <100 nodes)                      │
│  ├─ NetworkGraphCanvas.tsx (Canvas for >100 nodes)             │
│  ├─ useNetworkData.ts (data fetching)                          │
│  └─ graph_layout.ts (force simulation)                         │
│                                                                  │
│  🔴 Task 6: Heat Maps & Dashboard                               │
│  ├─ HeatMap.tsx (generic heat map component)                   │
│  ├─ RiskDashboard.tsx (3 heat maps + stats)                    │
│  ├─ heatmap_generator.ts (data aggregation)                    │
│  └─ export_utils.ts (PNG/PDF/CSV export)                       │
│                                                                  │
│  🔴 Task 7: Comparison & Selection                              │
│  ├─ ScenarioComparison.tsx (side-by-side view)                 │
│  ├─ ScenarioMatrix.tsx (sortable table)                        │
│  ├─ PortfolioBuilder.tsx (drag-and-drop)                       │
│  └─ Backend portfolio API                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sprint Sequencing Strategy

### Week 1: Backend Completion
1. **Days 1-3:** Task 4 (Scoring Engine)
   - Multi-factor algorithms
   - Confidence intervals
   - Calibration API
2. **Days 4-5:** Task 8a (Pipeline & API)
   - Phase 2 → Phase 3 orchestration
   - REST API endpoints
   - Basic integration tests

### Week 2-3: Frontend Foundation
3. **Days 6-10:** Task 5 (Network Visualization)
   - SVG graph (Day 6-7)
   - Canvas optimization (Day 8-9)
   - Interactivity & detail panel (Day 10)
4. **Days 11-15:** Task 6 (Heat Maps & Dashboard)
   - Heat map component (Day 11-12)
   - Dashboard integration (Day 13-14)
   - Export functionality (Day 15)
5. **Days 16-18:** Task 7 (Comparison & Selection)
   - Matrix view (Day 16)
   - Comparison view (Day 17)
   - Portfolio builder (Day 18)

### Week 4-5: Testing & Polish
6. **Days 19-25:** Task 8b (Comprehensive Testing)
   - Unit tests (Day 19-21)
   - Integration tests (Day 22-23)
   - CI/CD setup (Day 24)
   - Performance optimization (Day 25)

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Scoring Engine | ✅ Multi-factor with confidence intervals | 🔴 Not Started |
| Network Viz | ✅ <2s render for 100 nodes | 🔴 Not Started |
| Heat Maps | ✅ 3 interactive heat maps | 🔴 Not Started |
| Comparison UI | ✅ Side-by-side + matrix + portfolios | 🔴 Not Started |
| Pipeline | ✅ Automated Phase 2 → Phase 3 | 🔴 Not Started |
| Test Coverage | ✅ 90%+ unit + 10+ integration | 🔴 Not Started |
| **Overall** | **6/6** | **0/6** |

---

## Risk Assessment

### High Risk
- **Frontend Complexity**: Network visualization and heat maps are technically challenging
  - *Mitigation*: Use proven libraries (D3.js, React Flow), prioritize performance from start
- **LLM Costs**: Scoring engine may require many LLM calls
  - *Mitigation*: Cache results, use smaller models for sensitivity analysis

### Medium Risk
- **Testing Scope**: Comprehensive tests may take longer than estimated
  - *Mitigation*: Prioritize critical paths, use mocks to speed up tests
- **Integration Complexity**: Phase 2 → Phase 3 pipeline has many failure points
  - *Mitigation*: Extensive error handling, graceful degradation, monitoring

### Low Risk
- **API Development**: Straightforward CRUD endpoints
- **Portfolio Management**: Well-understood drag-and-drop patterns

---

## Dependencies

### External Dependencies
- **From Sprint 4 (Complete ✅):**
  - Database schema (phase3_schema.py)
  - Breach engine (breach_engine.py)
  - Counterfactual generator (counterfactual_generator.py)

### Required Libraries
- **Backend:**
  - `scipy` (bootstrap resampling)
  - `numpy` (numerical operations)
  - `networkx` (already installed for Task 3)
- **Frontend:**
  - `d3` (network visualization)
  - `react-flow` (alternative to D3)
  - `react-dnd` (drag-and-drop)
  - `html2canvas` (PNG export)
  - `jspdf` (PDF export)
  - `papaparse` (CSV export)

---

## Estimated Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Backend Completion | 1 week | Task 4, Task 8a |
| Frontend Foundation | 2-3 weeks | Task 5, Task 6, Task 7 |
| Testing & Integration | 1 week | Task 8b |
| **Total** | **4-5 weeks** | **5 tasks** |

---

## Next Steps

1. **Immediate (Day 1):**
   - Review Sprint 4 backend code
   - Set up development environment for Sprint 4.5
   - Install required libraries

2. **Week 1 Focus:**
   - Implement scoring engine (Task 4)
   - Create API endpoints (Task 8a)
   - Run database migrations (if schema changes needed)

3. **Week 2-3 Focus:**
   - Set up React/TypeScript frontend
   - Implement network visualization (Task 5)
   - Implement heat maps (Task 6)
   - Implement comparison interface (Task 7)

4. **Week 4-5 Focus:**
   - Comprehensive testing (Task 8b)
   - Performance optimization
   - Documentation
   - Deployment

---

## Conclusion

Sprint 4.5 builds upon the solid backend foundation from Sprint 4 to deliver a complete Phase 3 system with sophisticated scoring, rich visualizations, and seamless integration. The sprint focuses on user-facing features and production readiness, transforming the technical infrastructure into a powerful risk analysis tool.

**Key Deliverables:**
- Advanced multi-factor scoring with confidence intervals
- Interactive network visualization for 100+ nodes
- Comprehensive heat maps and dashboards
- Side-by-side comparison and portfolio management
- Fully automated Phase 2 → Phase 3 pipeline
- 90%+ test coverage with CI/CD

**Estimated Effort:** 152-192 hours (4-5 weeks)

---

**Generated**: October 13, 2025
**Sprint Owner**: Claude Code Agent
**Project**: Structured Reasoning System - Phase 3
**Status**: 🔴 NOT STARTED
**Dependencies**: Sprint 4 ✅ Complete
