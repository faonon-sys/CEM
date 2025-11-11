# Sprint 3 Quick Start Guide
## Phase 2: Deep Questioning Framework

**Last Updated**: October 13, 2025

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Sprint 1 & 2 completed (backend running)
- PostgreSQL database configured
- Anthropic API key set

### Start the System

```bash
# 1. Start backend (if not running)
cd backend
uvicorn main:app --reload --port 8000

# 2. Access API documentation
open http://localhost:8000/docs

# 3. Test deep questioning health
curl http://localhost:8000/api/deep-questions/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "validator": "operational",
    "question_engine": "operational",
    "fragility_detector": "operational"
  },
  "version": "2.0.0"
}
```

---

## 📋 Complete Workflow Example

### Step 1: Create a Scenario (if not exists)

```bash
# Create new scenario
curl -X POST http://localhost:8000/api/scenarios/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Taiwan Strait Crisis 2025",
    "description": "Military escalation following political tensions..."
  }'

# Save scenario_id from response
```

### Step 2: Validate Scenario Input

```bash
curl -X POST http://localhost:8000/api/scenarios/{scenario_id}/validate-input \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_text": "China announces naval exercises around Taiwan. US deploys carrier strike group. Taiwan raises alert level. Markets react with 5% drop. Assumes: stable US-China communication, no accidental escalation, rational actors, supply chain continuity..."
  }'
```

**Returns**:
- ✅ Validation result (pass/fail)
- 📝 Inline assumption preview (10+ candidates)
- 🏷️ Suggested domain tags (geopolitical, economic, etc.)
- 📊 Text quality metrics

### Step 3: Run Surface Analysis (Phase 1)

```bash
curl -X POST http://localhost:8000/api/scenarios/{scenario_id}/surface-analysis-v2 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Returns**: 12-15 extracted assumptions with quality scores

### Step 4: Generate Deep Questions (Phase 2)

```bash
curl -X POST http://localhost:8000/api/scenarios/{scenario_id}/generate-questions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "max_questions": 10,
    "dimension_filter": null
  }'
```

**Returns**: 10 prioritized questions across 4 dimensions

Example question:
```json
{
  "question_id": "q_temp_001_a3b2c4d5",
  "text": "If military mobilization is delayed by 3 months, what prevents diplomatic negotiations from proceeding?",
  "dimension": "temporal",
  "rationale": "This question probes timeline dependencies and sequence assumptions...",
  "priority_score": 0.85
}
```

### Step 5: Submit Responses & Analyze Fragility

```bash
curl -X POST http://localhost:8000/api/scenarios/{scenario_id}/analyze-fragility \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      {
        "question_id": "q_temp_001_a3b2c4d5",
        "response_text": "There are no formal backup communication channels. Diplomatic corps is understaffed. Previous delays have led to misunderstandings.",
        "confidence": 0.6
      }
    ]
  }'
```

**Returns**: Fragility analysis with scores, breach probabilities, recommendations

### Step 6: Export Results

```bash
# JSON export
curl http://localhost:8000/api/scenarios/{scenario_id}/deep-analysis/export?format=json \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  > analysis.json

# Markdown export
curl http://localhost:8000/api/scenarios/{scenario_id}/deep-analysis/export?format=markdown \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  > analysis.md
```

---

## 📚 Key Features

### 1. Question Template Library (60 Templates)

| Dimension | Count | Focus |
|-----------|-------|-------|
| **Temporal** | 15 | Timeline dependencies, sequence disruption |
| **Structural** | 15 | System architecture, single points of failure |
| **Actor-Based** | 15 | Motivations, capabilities, incentive alignment |
| **Resource-Based** | 15 | Availability, allocation, constraints |

**Browse templates**:
```python
from services.question_templates import template_library

# Get all templates
templates = template_library.get_all_templates()

# Get by dimension
temporal_templates = template_library.get_by_dimension("temporal")

# Search
results = template_library.search_templates("timeline")

# Statistics
stats = template_library.get_statistics()
```

### 2. Fragility Scoring Algorithm

**Formula**:
```
Fragility Score (1-10) = 10 × (
  0.4 × evidence_weakness +
  0.3 × dependency_count +
  0.2 × response_uncertainty +
  0.1 × breach_likelihood
)
```

**Severity Labels**:
- 🔴 **Critical**: 8.0-10.0 (immediate attention)
- ⚠️ **High**: 6.0-7.9 (contingency plans needed)
- 🟡 **Medium**: 4.0-5.9 (monitor closely)
- 🟢 **Low**: 0.0-3.9 (acceptable risk)

### 3. Scenario Templates

Get quick-start templates:
```bash
curl http://localhost:8000/api/scenarios/templates \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Available Templates**:
1. 🌍 Geopolitical Crisis
2. 💻 Technology Disruption
3. 📈 Market Analysis
4. 🌡️ Climate/Environmental Event
5. 🏥 Public Health Crisis

---

## 🔧 Configuration Options

### Question Generation

```python
# Customize generation
{
  "max_questions": 12,  # 1-20
  "dimension_filter": "temporal",  # null, temporal, structural, actor_based, resource_based
  "validate_consistency": true  # Enable/disable consistency checks
}
```

### Fragility Analysis

```python
# Response format
{
  "question_id": "q_...",
  "response_text": "Detailed answer...",  # 20-500 words recommended
  "confidence": 0.7  # 0.0-1.0 scale
}
```

**Tips for Better Analysis**:
- ✅ Provide detailed responses (50+ words)
- ✅ Include specific data/evidence
- ✅ Mention uncertainty honestly
- ✅ Reference sources when possible
- ❌ Avoid very short responses (<20 words)
- ❌ Don't leave confidence at default

---

## 📊 Understanding Results

### Fragility Point Example

```json
{
  "assumption_id": "assumption_5",
  "fragility_score": 8.2,
  "breach_probability": 0.65,
  "impact_radius": ["assumption_2", "assumption_7"],
  "evidence_gaps": [
    "no data on historical precedent",
    "unclear monitoring capability"
  ],
  "markers": [
    {"type": "uncertainty", "text": "unclear", "position": 45}
  ],
  "severity": "critical"
}
```

**Interpretation**:
- **8.2 score**: Critical fragility - immediate attention needed
- **65% breach probability**: High likelihood assumption will fail
- **Impact radius**: Failure cascades to 2 other assumptions
- **Evidence gaps**: Specific areas lacking support
- **Markers**: Linguistic uncertainty detected in response

### Recommendations Example

```json
{
  "recommendations": [
    "🚨 2 critical fragility points require immediate attention",
    "⚠️  3 high-severity fragilities need contingency plans",
    "🔗 4 assumptions have large impact radius (cascading risk)",
    "📊 14 evidence gaps identified - gather additional data"
  ]
}
```

---

## 🐛 Troubleshooting

### Issue: "No surface analysis found"

**Solution**: Run Phase 1 first
```bash
curl -X POST http://localhost:8000/api/scenarios/{scenario_id}/surface-analysis-v2 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Issue: Questions seem generic

**Solution**: Ensure surface analysis has quality assumptions
- Check assumption confidence scores (>0.5)
- Verify domain categorization
- Use dimension_filter to focus

### Issue: Fragility scores all low

**Solution**: Provide more detailed responses
- Include uncertainty markers naturally
- Mention evidence gaps explicitly
- Use confidence slider accurately (don't default to 1.0)

### Issue: LLM context extraction fails

**Solution**: System automatically falls back to heuristics
- Check logs for fallback messages
- Verify ANTHROPIC_API_KEY is set
- Ensure scenario text is 100+ characters

---

## 📈 Performance Tips

### Optimize Question Generation

```python
# Start with fewer questions for testing
{"max_questions": 5}  # Faster generation

# Use dimension filter for focused analysis
{"dimension_filter": "structural"}  # 3-4 questions only

# Disable consistency validation for speed
{"validate_consistency": false}  # Saves 5-8 seconds
```

### Batch Operations

```python
# Validate multiple assumptions at once
{
  "actions": [
    {"assumption_id": "assumption_1", "action": "accept"},
    {"assumption_id": "assumption_2", "action": "reject"},
    {"assumption_id": "assumption_3", "action": "edit", "new_text": "Updated..."}
  ]
}
```

---

## 🔗 API Endpoint Quick Reference

| Endpoint | Method | Purpose | Time |
|----------|--------|---------|------|
| `/scenarios/{id}/validate-input` | POST | Validate scenario text | <1s |
| `/scenarios/templates` | GET | Get templates | <1s |
| `/scenarios/{id}/generate-questions` | POST | Generate questions | 10-20s |
| `/scenarios/{id}/analyze-fragility` | POST | Analyze responses | 5-10s |
| `/scenarios/{id}/assumptions/validate-batch` | POST | Batch validate | <1s |
| `/scenarios/{id}/deep-analysis/export` | GET | Export results | <2s |
| `/deep-questions/health` | GET | Health check | <1s |

---

## 🎯 Best Practices

### Question Answering

1. **Be Specific**
   - ✅ "Historical data from 1995-2010 shows 3/5 similar crises escalated..."
   - ❌ "It might escalate"

2. **Acknowledge Uncertainty**
   - ✅ "Unclear if backup systems exist; no documentation found"
   - ❌ "Yes, definitely" (when uncertain)

3. **Cite Evidence**
   - ✅ "According to NATO report 2024, capacity is 40% of required..."
   - ❌ "Capacity is adequate"

4. **Use Confidence Slider**
   - 0.9-1.0: Very confident, strong evidence
   - 0.7-0.8: Confident, some evidence
   - 0.5-0.6: Moderate uncertainty
   - 0.0-0.4: High uncertainty, weak evidence

### Scenario Design

1. **Length**: 500-2000 words optimal
2. **Structure**: Clear narrative with stated assumptions
3. **Specificity**: Include numbers, dates, actors, resources
4. **Domains**: Tag 2-4 relevant domains
5. **Assumptions**: Make some explicit for testing

---

## 📖 Example Scenarios

### Geopolitical Crisis

```
Title: Taiwan Strait Escalation 2025

China announces 30-day military exercises encircling Taiwan following
US congressional delegation visit. US deploys two carrier strike groups
to region. Japan raises defense readiness to Level 3. South Korea
remains neutral. Taiwan mobilizes reserves.

Key Assumptions:
- US-China hotline remains functional
- No accidental engagements occur
- Rational actor theory holds
- Supply chains (semiconductors) remain stable
- International law governs behavior
- Regional allies coordinate effectively
- Economic costs deter escalation
- Domestic politics allow de-escalation
```

### Technology Disruption

```
Title: Enterprise AI Adoption Wave 2025

Fortune 500 companies rapidly deploying GPT-5 for knowledge work.
40% of analyst roles automated in 18 months. Regulatory framework
lags by 2-3 years. Incumbent workers resist; unions negotiate.

Key Assumptions:
- AI accuracy exceeds 95% for routine tasks
- Regulatory capture doesn't stall deployment
- Worker retraining scales at required pace
- Economic benefits distributed broadly
- No catastrophic AI failure occurs
- Infrastructure scales to meet demand
```

---

## 🔄 Integration with Other Phases

```
Phase 1 (Surface Analysis)
      ↓
  Extracts 12-15 assumptions with categories
      ↓
Phase 2 (Deep Questioning) ← YOU ARE HERE
      ↓
  Generates 10 probing questions
  Identifies 3-8 fragility points
  Maps evidence gaps
      ↓
Phase 3 (Counterfactual Generation) - FUTURE
      ↓
  Uses fragilities to seed breach conditions
  Maps to strategic axes
  Generates alternative scenarios
```

**Data Flow**:
- Phase 1 assumptions → Phase 2 question targets
- Phase 2 fragilities → Phase 3 breach conditions
- Phase 2 impact radius → Phase 3 cascade analysis

---

## 💡 Pro Tips

1. **Question Selection**: Start with structural dimension for foundation
2. **Response Depth**: 50-100 words per response is optimal
3. **Confidence Calibration**: Use full 0-1 scale; avoid defaulting to 0.5
4. **Iterative Refinement**: Run analysis 2-3 times with refined responses
5. **Export Early**: Save JSON/Markdown after each session
6. **Dimension Focus**: Use filters for targeted deep dives
7. **Template Exploration**: Browse template library for insight patterns

---

## 📞 Support

### Documentation
- Full completion report: `SPRINT_3_COMPLETION.md`
- API docs: http://localhost:8000/docs
- Project structure: `PROJECT_STRUCTURE.txt`

### Common Questions

**Q: How many questions should I answer?**
A: Minimum 5 for basic analysis, 10-12 for comprehensive insights

**Q: Can I skip questions?**
A: Yes, but analysis quality degrades. Answer high-priority questions first.

**Q: What if I don't know the answer?**
A: Be honest! Say "unclear" or "no data" - this creates valuable evidence gaps.

**Q: How long does full analysis take?**
A: 20-30 minutes for scenario input + question answering + review

**Q: Can I export and continue later?**
A: Yes, all data persists in PostgreSQL. Export JSON to save state.

---

## 🚀 Next Steps

After completing Phase 2:

1. ✅ Review fragility analysis recommendations
2. ✅ Export results (JSON + Markdown)
3. ✅ Share with stakeholders for feedback
4. ✅ Prepare for Phase 3 (Counterfactual Generation)
5. ✅ Iterate: refine responses and re-analyze

---

**Generated**: October 13, 2025
**Version**: 2.0.0
**Status**: Production Ready
