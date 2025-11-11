# Sprint 2.5 Quick Start Guide

Get started with the Surface Analysis UI in 5 minutes.

---

## Prerequisites

1. **Backend Running** (from Sprint 2):
   ```bash
   cd /Users/raminhedayatpour/Documents/VibeProjects/test/backend
   uvicorn main:app --reload --port 8000
   ```

2. **Environment Variables Set**:
   ```bash
   ANTHROPIC_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:pass@localhost:5432/structured_reasoning
   ```

---

## Quick Start (2 Steps)

### Step 1: Start Frontend

```bash
cd /Users/raminhedayatpour/Documents/VibeProjects/test/frontend/react-app

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

Frontend runs on: http://localhost:5173

### Step 2: Access Surface Analysis UI

Open browser: http://localhost:5173/surface-analysis/123e4567-e89b-12d3-a456-426614174000

(Replace `123e4567-e89b-12d3-a456-426614174000` with your actual scenario ID)

---

## Usage Guide

### Generate Your First Analysis

1. **Navigate to Surface Analysis**:
   - Click "Surface Analysis" in navigation
   - Or visit: `/surface-analysis/{your-scenario-id}`

2. **Generate Analysis**:
   - Click "Generate Analysis" button
   - Wait 50-100 seconds (progress shown)
   - Dashboard and assumptions appear

3. **Explore Results**:
   - View summary metrics in dashboard
   - Scroll through assumption cards
   - Click "Expand Details" on any card

### Filter Assumptions

1. **Open Filter Panel** (top of page)

2. **Select Domains**:
   - Check "Political" and "Economic"
   - Results update automatically

3. **Set Priority**:
   - Select "High" radio button
   - Only high-priority assumptions shown

4. **Adjust Quality Threshold**:
   - Drag slider to 70
   - Only assumptions with quality ≥70 shown

5. **View Results**:
   - "Showing: 3 of 12 assumptions"

6. **Clear Filters**:
   - Click "Clear All" button

### Validate Assumptions

#### Single Assumption

1. Expand assumption card
2. Review quality breakdown and source
3. Click "Accept" or "Reject"
4. See green/red toast notification
5. "✓ Validated" badge appears

#### Batch Operations

1. Check 3 assumption checkboxes
2. Toolbar appears: "3 selected"
3. Click "Accept Selected (3)"
4. Confirm in dialog
5. All 3 assumptions validated
6. Toast: "3 assumptions accepted"

### Export Results

1. Click "Export JSON" or "Export Markdown"
2. File downloads automatically
3. Filename: `scenario_{id}_analysis.{json|md}`
4. Open in editor to review

---

## Component Overview

### 1. Analysis Dashboard
- **Location**: Top of page
- **Shows**: Metrics, priority breakdown, domain distribution
- **Use**: Get overview of analysis quality

### 2. Filter Panel
- **Location**: Below dashboard
- **Controls**: Domains, priority, quality slider
- **Use**: Narrow down assumptions to review

### 3. Batch Actions Toolbar
- **Location**: Above assumption list (when selections made)
- **Controls**: Select all, accept/reject selected, clear
- **Use**: Process multiple assumptions at once

### 4. Assumption Cards
- **Location**: Main content area
- **Features**:
  - Priority badge, quality score
  - Domain badges
  - Confidence bar
  - Expandable details
  - Accept/Reject buttons
- **Use**: Review and validate individual assumptions

### 5. Export Buttons
- **Location**: Top right of page
- **Buttons**: Export JSON, Export Markdown
- **Use**: Download analysis for sharing/archiving

---

## Keyboard Shortcuts

(Future enhancement - currently mouse-driven)

---

## Troubleshooting

### Issue: "No analysis found" Error

**Solution**: Click "Generate Analysis" to create new analysis

**Cause**: Scenario exists but hasn't been analyzed yet

---

### Issue: Analysis Takes Too Long (>2 minutes)

**Possible Causes**:
- Backend not running
- LLM API rate limit reached
- Network timeout

**Solutions**:
1. Check backend is running: `curl http://localhost:8000/`
2. Check Anthropic API key is valid
3. Check backend logs for errors

---

### Issue: Filters Don't Work

**Solution**:
- If API filter fails, client-side filtering activates automatically
- Check browser console for errors
- Verify backend `/assumptions/filter` endpoint responds

---

### Issue: Export Downloads Empty File

**Possible Causes**:
- Analysis hasn't been generated
- Backend export endpoint error

**Solutions**:
1. Ensure analysis is loaded (dashboard visible)
2. Check backend logs for export errors
3. Try other format (JSON vs Markdown)

---

### Issue: Batch Accept/Reject Not Working

**Solution**:
- Ensure assumptions are selected (checkboxes checked)
- Click "Confirm" in dialog (don't click outside)
- Check backend logs for validation errors

---

## Features Reference

| Feature | Location | Shortcut | API Endpoint |
|---------|----------|----------|--------------|
| Generate Analysis | Header button | - | POST `/scenarios/{id}/surface-analysis-v2` |
| View Analysis | Auto-load | - | GET `/scenarios/{id}/surface-analysis-v2` |
| Filter Domains | Filter panel | - | GET `/scenarios/{id}/assumptions/filter` |
| Filter Priority | Filter panel | - | GET `/scenarios/{id}/assumptions/filter` |
| Filter Quality | Filter panel | - | GET `/scenarios/{id}/assumptions/filter` |
| Accept Assumption | Card button | - | POST `/scenarios/{id}/assumptions/validate` |
| Reject Assumption | Card button | - | POST `/scenarios/{id}/assumptions/validate` |
| Batch Accept | Toolbar button | - | POST `/scenarios/{id}/assumptions/validate` |
| Batch Reject | Toolbar button | - | POST `/scenarios/{id}/assumptions/validate` |
| Export JSON | Header button | - | GET `/scenarios/{id}/export/json` |
| Export Markdown | Header button | - | GET `/scenarios/{id}/export/markdown` |

---

## Example Workflow

### Scenario: Federal Reserve Rate Decision

1. **Create Scenario** (in Swagger UI or separate tool):
   ```json
   {
     "title": "Federal Reserve Rate Decision Q3 2024",
     "description": "The Federal Reserve is expected to raise rates by 0.25% at the March 2024 FOMC meeting..."
   }
   ```
   Copy returned `scenario_id`

2. **Navigate to Surface Analysis**:
   ```
   http://localhost:5173/surface-analysis/{scenario_id}
   ```

3. **Generate Analysis**:
   - Click "Generate Analysis"
   - Wait 50-100 seconds
   - 12 assumptions extracted

4. **Review High-Priority Assumptions**:
   - Filter: Priority = "High"
   - Result: 5 high-priority assumptions
   - Review each: quality scores, domains, confidence

5. **Validate Assumptions**:
   - Expand assumption #1: "Fed will raise rates by 0.25%"
   - Quality: 85/100 (High)
   - Confidence: 90%
   - Source: "Fed statement dated March 15, 2024"
   - Click "Accept"

6. **Batch Validate Rest**:
   - Select remaining 4 high-priority assumptions
   - Click "Accept Selected (4)"
   - Confirm

7. **Export Results**:
   - Click "Export Markdown"
   - Share with team for review

---

## Next Steps

After completing Sprint 2.5:

1. **Sprint 3: Deep Questioning**
   - Feed high-priority assumptions from Surface Analysis
   - Generate probing questions to expose vulnerabilities

2. **Sprint 4: Phase 3 Pipeline**
   - Use validated assumptions for counterfactual generation
   - Visualize assumption → fragility → breach → counterfactual flow

3. **Sprint 5+: Advanced Visualizations**
   - Interactive relationship graph (D3.js)
   - Quality trend charts (Chart.js)
   - Comparison across scenarios

---

## Support

- **API Documentation**: http://localhost:8000/docs
- **Sprint 2.5 Completion Report**: SPRINT_2.5_COMPLETION.md
- **Sprint 2.5 Plan**: SPRINT_2.5_PLAN.md
- **Backend Documentation**: SPRINT_2_COMPLETION.md

---

**Last Updated**: October 17, 2025
**Sprint 2.5 Version**: 1.0
