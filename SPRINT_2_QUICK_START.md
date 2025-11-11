# Sprint 2 Quick Start Guide

Get started with the enhanced Surface Premise Analysis Engine in 5 minutes.

---

## Prerequisites

1. **Environment Setup** (from Sprint 1):
   ```bash
   cd /Users/raminhedayatpour/Documents/VibeProjects/test
   ```

2. **Environment Variables**:
   ```bash
   # Create .env file
   cp .env.example .env

   # Edit .env and add:
   ANTHROPIC_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:pass@localhost:5432/structured_reasoning
   ```

3. **Dependencies** (if not already installed):
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

---

## Quick Start (3 Steps)

### Step 1: Start Services

```bash
# Terminal 1: Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Terminal 2: Start Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 3: Start Frontend (optional)
cd frontend
streamlit run streamlit_app/main.py --server.port 5000
```

### Step 2: Access API Documentation

Open browser: http://localhost:8000/docs

You'll see the new Sprint 2 endpoints under **"Phase 1: Surface Analysis V2 (Sprint 2)"**

### Step 3: Run Your First Analysis

#### Option A: Using Swagger UI (http://localhost:8000/docs)

1. **Authenticate**:
   - POST `/api/auth/register` - Create account
   - POST `/api/auth/login` - Get JWT token
   - Click "Authorize" button, enter: `Bearer YOUR_TOKEN`

2. **Create Scenario**:
   - POST `/api/scenarios/`
   ```json
   {
     "title": "Federal Reserve Rate Decision",
     "description": "The Federal Reserve is expected to maintain interest rates at current levels throughout 2024, assuming inflation continues to decline. This policy stance depends on stable employment figures and no major geopolitical disruptions. Market participants believe this will support continued economic growth."
   }
   ```
   - Copy the returned `id`

3. **Generate Analysis**:
   - POST `/api/scenarios/{id}/surface-analysis-v2`
   - Query params: `validate_consistency=true`, `detect_relationships=true`
   - Wait 50-100 seconds for complete analysis

4. **View Results**:
   - GET `/api/scenarios/{id}/surface-analysis-v2`
   - See enriched assumptions with quality scores, domains, priorities

5. **Filter Assumptions**:
   - GET `/api/scenarios/{id}/assumptions/filter`
   - Params: `domains=economic&priority=high&min_quality=70`

6. **Export Results**:
   - GET `/api/scenarios/{id}/export/json` - Download JSON
   - GET `/api/scenarios/{id}/export/markdown` - Download report

#### Option B: Using cURL

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword",
    "full_name": "Test User"
  }'

# 2. Login (save token)
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword" \
  | jq -r '.access_token')

# 3. Create Scenario
SCENARIO_ID=$(curl -X POST "http://localhost:8000/api/scenarios/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Scenario",
    "description": "The Federal Reserve is expected to maintain interest rates..."
  }' | jq -r '.id')

# 4. Generate Analysis
curl -X POST "http://localhost:8000/api/scenarios/$SCENARIO_ID/surface-analysis-v2?validate_consistency=true&detect_relationships=true" \
  -H "Authorization: Bearer $TOKEN"

# 5. Get Results
curl -X GET "http://localhost:8000/api/scenarios/$SCENARIO_ID/surface-analysis-v2" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 6. Export Markdown
curl -X GET "http://localhost:8000/api/scenarios/$SCENARIO_ID/export/markdown" \
  -H "Authorization: Bearer $TOKEN" \
  -o analysis_report.md
```

#### Option C: Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. Register and Login
register_data = {
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword",
    "full_name": "Test User"
}
requests.post(f"{BASE_URL}/auth/register", json=register_data)

login_data = {"username": "user@example.com", "password": "securepassword"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Create Scenario
scenario_data = {
    "title": "Federal Reserve Rate Decision",
    "description": "The Federal Reserve is expected to maintain interest rates..."
}
response = requests.post(f"{BASE_URL}/scenarios/", json=scenario_data, headers=headers)
scenario_id = response.json()["id"]

# 3. Generate Analysis (with progress monitoring)
print("Generating analysis... (this takes 50-100 seconds)")
response = requests.post(
    f"{BASE_URL}/scenarios/{scenario_id}/surface-analysis-v2",
    params={"validate_consistency": True, "detect_relationships": True},
    headers=headers,
    timeout=180
)
analysis = response.json()

print(f"Analysis complete! Found {len(analysis['assumptions']['assumptions'])} assumptions")

# 4. Filter High-Priority Assumptions
response = requests.get(
    f"{BASE_URL}/scenarios/{scenario_id}/assumptions/filter",
    params={"priority": "high", "min_quality": 70},
    headers=headers
)
high_priority = response.json()
print(f"High-priority assumptions: {high_priority['filtered_assumptions']}")

# 5. Export as JSON
response = requests.get(
    f"{BASE_URL}/scenarios/{scenario_id}/export/json",
    headers=headers
)
with open("analysis.json", "w") as f:
    f.write(response.text)

# 6. Export as Markdown
response = requests.get(
    f"{BASE_URL}/scenarios/{scenario_id}/export/markdown",
    headers=headers
)
with open("analysis_report.md", "w") as f:
    f.write(response.text)

print("Done! Check analysis.json and analysis_report.md")
```

---

## Understanding the Output

### Assumption Structure

Each assumption is enriched with:

```json
{
  "id": "assumption_1",
  "text": "The Federal Reserve will maintain rates throughout 2024",
  "source_excerpt": "expected to maintain interest rates at current levels",
  "domains": ["economic", "political"],
  "domain_confidence": {
    "economic": 0.85,
    "political": 0.65
  },
  "is_cross_domain": true,
  "quality_score": 78.5,
  "quality_dimensions": {
    "specificity": 75.0,
    "verifiability": 80.0,
    "impact_potential": 85.0,
    "source_strength": 70.0
  },
  "priority_tier": "high",
  "confidence": 0.85,
  "validated": false,
  "user_edited": false
}
```

### Priority Tiers

- 🔴 **High**: Quality ≥ 70, Confidence ≥ 0.7 (focus here first)
- ⚠️ **Needs Review**: Confidence < 0.5 (manual review recommended)
- 🟡 **Medium**: Quality 40-70 (standard assumptions)
- 🟢 **Low**: Quality < 40 (less critical)

### Relationship Types

- **depends_on**: A requires B (if B fails, A cannot hold)
- **contradicts**: A and B are mutually exclusive
- **reinforces**: A strengthens B (they support each other)

---

## Common Workflows

### Workflow 1: Basic Analysis

```
1. Create Scenario
2. Generate Analysis
3. Review High-Priority Assumptions
4. Export Report
```

### Workflow 2: Iterative Refinement

```
1. Create Scenario
2. Generate Analysis (no relationships for speed)
3. Review & Validate Assumptions (accept/reject/edit)
4. Regenerate with Relationships
5. Export Final Report
```

### Workflow 3: Comparative Analysis

```
1. Create Multiple Scenarios (variations)
2. Generate Analysis for Each
3. Filter by Domain (e.g., "economic")
4. Compare Assumptions Across Scenarios
5. Identify Common Patterns
```

### Workflow 4: Deep Dive

```
1. Generate Analysis with Relationships
2. Identify Critical Assumptions (graph analysis)
3. Examine Circular Dependencies
4. Review Contradiction Pairs
5. Focus Deep Questioning on Critical Nodes
```

---

## API Endpoint Reference

### Analysis Generation

```
POST /api/scenarios/{id}/surface-analysis-v2
  ?validate_consistency=true    # Optional: Run dual extraction
  ?detect_relationships=true    # Optional: Build dependency graph

Time: 50-100 seconds (full pipeline)
      20-30 seconds (no relationships)
```

### Assumption Filtering

```
GET /api/scenarios/{id}/assumptions/filter
  ?domains=political,economic   # Filter by domains (comma-separated)
  ?priority=high                # Filter by priority tier
  ?min_quality=70               # Minimum quality score

Returns: Filtered list with counts
```

### Batch Validation

```
POST /api/scenarios/{id}/assumptions/validate

Body: [
  {"assumption_id": "assumption_1", "action": "accept"},
  {"assumption_id": "assumption_2", "action": "reject"},
  {"assumption_id": "assumption_3", "action": "edit", "new_text": "Updated"}
]
```

### Export

```
GET /api/scenarios/{id}/export/json       # JSON export
GET /api/scenarios/{id}/export/markdown   # Markdown report
```

---

## Performance Tips

### 1. Speed Up Analysis

```python
# Skip consistency validation for faster results
POST /surface-analysis-v2?validate_consistency=false

# Skip relationships if not needed
POST /surface-analysis-v2?detect_relationships=false

Time saved: 30-40 seconds
```

### 2. Efficient Filtering

```python
# Filter before fetching full details
GET /assumptions/filter?priority=high

# Then fetch full assumptions for filtered IDs only
```

### 3. Batch Operations

```python
# Validate multiple assumptions at once
POST /assumptions/validate
[
  {"assumption_id": "...", "action": "accept"},
  {"assumption_id": "...", "action": "accept"},
  ...
]
```

---

## Troubleshooting

### Issue: Analysis Takes Too Long

**Solution**: Disable relationships or consistency validation
```
POST /surface-analysis-v2?detect_relationships=false&validate_consistency=false
```

### Issue: No Assumptions Extracted

**Possible Causes**:
- Scenario text too short (< 200 words)
- Scenario text too vague or generic
- LLM API issues

**Solution**: Provide more detailed scenario (500-1000 words recommended)

### Issue: Low Consistency Score

**Meaning**: Extractions differ significantly between runs

**Action**: Review assumptions manually, may indicate ambiguous scenario

**Threshold**: < 0.75 triggers warning

### Issue: No Relationships Found

**Possible Causes**:
- Assumptions are too independent
- Domain filtering removed all pairs
- Confidence threshold too high

**Solution**: This is normal for some scenarios - not all assumptions are related

---

## Example Scenarios

### Good Scenario (Detailed, Specific)

```
The Federal Reserve is expected to raise interest rates by 0.25% at the
March 2024 FOMC meeting, based on recent inflation data showing a decline
to 3.2% year-over-year. Market analysts predict this will slow mortgage
lending by approximately 10% and potentially trigger a mild recession by
Q3 2024. The assumption is that the labor market remains resilient with
unemployment staying below 4%, and that no major geopolitical disruptions
occur in the energy sector. Congressional pressure for lower rates is
expected to be manageable given the Fed's independence.
```

**Why Good**:
- Specific numbers (0.25%, 3.2%, 10%, 4%)
- Clear timeframes (March 2024, Q3 2024)
- Named entities (Federal Reserve, FOMC)
- Multiple domains (economic, political)
- Observable consequences

### Poor Scenario (Vague, Generic)

```
Things are expected to get better in the economy. The government will
probably do something about inflation. Markets might respond positively.
```

**Why Poor**:
- No specific numbers or dates
- Vague language ("probably", "might")
- No named entities
- No clear assumptions to extract

---

## Next Steps

1. **Explore Relationships**:
   ```python
   # Check dependency graph
   analysis['relationships']['graph_analysis']['critical_assumptions']
   ```

2. **Use for Phase 2**:
   ```python
   # Feed high-priority assumptions to Deep Questioning
   GET /scenarios/{id}/deep-questions
   ```

3. **Build Dashboards**:
   - Visualize domain distribution
   - Track quality scores over time
   - Show relationship graphs

4. **Integrate with Phase 3**:
   - Use critical assumptions for counterfactual generation
   - Breach anchor assumptions to explore alternative scenarios

---

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **Sprint 2 Completion Report**: SPRINT_2_COMPLETION.md
- **Architecture Details**: PROJECT_STRUCTURE.txt
- **Original Requirements**: (see execution plan in prompt)

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│              SPRINT 2 QUICK REFERENCE                   │
├─────────────────────────────────────────────────────────┤
│ Generate Analysis:                                       │
│   POST /scenarios/{id}/surface-analysis-v2              │
│                                                          │
│ Filter Assumptions:                                      │
│   GET /scenarios/{id}/assumptions/filter                │
│   ?domains=X&priority=Y&min_quality=Z                   │
│                                                          │
│ Validate Assumptions:                                    │
│   POST /scenarios/{id}/assumptions/validate             │
│   Body: [{assumption_id, action}]                       │
│                                                          │
│ Export Results:                                          │
│   GET /scenarios/{id}/export/json                       │
│   GET /scenarios/{id}/export/markdown                   │
│                                                          │
│ Priority Tiers:                                          │
│   🔴 high      (quality ≥70, conf ≥0.7)                 │
│   ⚠️  needs_review (confidence <0.5)                     │
│   🟡 medium    (quality 40-70)                           │
│   🟢 low       (quality <40)                             │
│                                                          │
│ Relationship Types:                                      │
│   depends_on   (A requires B)                           │
│   contradicts  (A ↔ B mutually exclusive)               │
│   reinforces   (A ↔ B support each other)               │
└─────────────────────────────────────────────────────────┘
```

---

**Last Updated**: October 13, 2025
**Sprint 2 Version**: 2.0

