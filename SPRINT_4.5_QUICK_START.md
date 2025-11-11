# Sprint 4.5 Quick Start Guide
## Scoring, Visualization & Calibration System

**Last Updated**: October 16, 2025
**Prerequisites**: Sprint 1-4 completed, PostgreSQL running, Python 3.11+, Node.js 18+

---

## 🚀 5-Minute Quick Start

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install numpy==1.26.2 scipy==1.11.4
pip install -r requirements.txt
```

### Step 2: Run Database Migration

```bash
# Apply Sprint 4.5 scoring tables migration
alembic upgrade head

# Verify migration
psql -d structured_reasoning -c "\d counterfactual_scores"
```

### Step 3: Start Backend Server

```bash
# From backend directory
uvicorn main:app --reload --port 8000

# Verify scoring endpoints
curl http://localhost:8000/docs
# Navigate to "Sprint 4.5: Scoring System" section
```

### Step 4: Install Frontend Dependencies

```bash
cd frontend/react-app
npm install
```

### Step 5: Start React Development Server

```bash
npm run dev

# Opens on http://localhost:5173
# Proxies API calls to http://localhost:8000
```

### Step 6: Access the Application

```
🌐 Frontend UI:     http://localhost:5173
📚 API Docs:        http://localhost:8000/docs
🗄️ Database:        localhost:5432/structured_reasoning
```

---

## 📊 Testing the Scoring System

### 1. Create Test Counterfactual (via API)

```bash
# Login to get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}' \
  | jq -r '.access_token')

# Create scenario
SCENARIO_ID=$(curl -X POST http://localhost:8000/api/scenarios/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Scenario",
    "description": "Testing Sprint 4.5 scoring"
  }' | jq -r '.id')

# Create counterfactual
CF_ID=$(curl -X POST http://localhost:8000/api/scenarios/$SCENARIO_ID/counterfactuals \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "axis": "economic_axis",
    "breach_condition": "Major trade sanctions imposed",
    "consequences": [
      {"description": "Supply chain disruption", "domains": ["economic", "political"]},
      {"description": "Inflation spike", "domains": ["economic"]}
    ],
    "severity_rating": 8,
    "probability_rating": 0.6
  }' | jq -r '.id')
```

### 2. Compute Scores

```bash
curl -X POST http://localhost:8000/api/scoring/compute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"counterfactual_ids\": [\"$CF_ID\"],
    \"force_recompute\": false
  }" | jq '.'
```

**Expected Response:**
```json
{
  "scores": [{
    "id": "...",
    "counterfactual_id": "...",
    "severity": {
      "score": 0.752,
      "confidence_interval": [0.698, 0.809],
      "factors": {
        "cascade_depth": 0.226,
        "breadth_of_impact": 0.188,
        "deviation_magnitude": 0.200,
        "irreversibility": 0.138
      },
      "sensitivity": {
        "cascade_depth": 0.300,
        "breadth_of_impact": 0.250,
        ...
      }
    },
    "probability": {
      "score": 0.568,
      ...
    },
    "risk_score": 0.427
  }],
  "computation_time": 0.234,
  "message": "Computed scores for 1 counterfactuals..."
}
```

### 3. Retrieve Score

```bash
curl -X GET http://localhost:8000/api/scoring/$CF_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 4. Run Sensitivity Analysis

```bash
curl -X GET http://localhost:8000/api/scoring/sensitivity/$CF_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

**Response shows which factors influence score most:**
```json
{
  "severity_sensitivity": {
    "cascade_depth": 0.300,
    "breadth_of_impact": 0.250,
    "deviation_magnitude": 0.250,
    "irreversibility": 0.200
  },
  "most_influential_factors": {
    "severity": "cascade_depth",
    "probability": "fragility_strength"
  }
}
```

### 5. Run Monte Carlo Simulation

```bash
curl -X POST http://localhost:8000/api/scoring/monte-carlo \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"counterfactual_id\": \"$CF_ID\",
    \"n_simulations\": 10000
  }" | jq '.risk'
```

**Response includes risk distribution:**
```json
{
  "risk": {
    "mean": 0.428,
    "std": 0.053,
    "percentiles": {
      "p5": 0.341,
      "p25": 0.392,
      "p50": 0.427,
      "p75": 0.463,
      "p95": 0.520
    }
  }
}
```

### 6. Calibrate Score (Expert Adjustment)

```bash
curl -X PUT http://localhost:8000/api/scoring/calibrate/$CF_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "severity_adjustment": 0.85,
    "probability_adjustment": 0.55,
    "rationale": "Domain expertise suggests higher severity but lower probability due to diplomatic pressure"
  }' | jq '.'
```

### 7. Check Calibration Statistics

```bash
curl -X GET http://localhost:8000/api/scoring/calibration/statistics \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 🎨 Using the React Visualization

### Network Graph View

1. Navigate to http://localhost:5173/
2. The network graph displays sample data by default
3. **Interactions:**
   - **Zoom**: Scroll wheel
   - **Pan**: Click and drag background
   - **Select Node**: Click on any node
   - **Filter**: Use controls in top-left panel
   - **View Details**: Click node to open detail panel

### Dashboard View

1. Navigate to http://localhost:5173/dashboard
2. View heat maps and summary statistics
3. Current status: Placeholder components (Recharts integration pending)

### Comparison View

1. Navigate to http://localhost:5173/comparison
2. Compare multiple scenarios side-by-side
3. View overlap analysis
4. Build portfolios for Phase 5 (drag-and-drop pending)

### Calibration Interface

1. Navigate to http://localhost:5173/calibration
2. Select scenario to calibrate
3. Adjust severity and probability scores
4. View factor contributions
5. Add rationale and save

---

## 🔧 Configuration

### Custom Scoring Weights

```python
# In Python
from backend.services.scoring_engine import ScoringEngine

# Custom weights (must sum to 1.0)
custom_weights = {
    'severity_weights': {
        'cascade_depth': 0.40,        # Increased importance
        'breadth_of_impact': 0.30,
        'deviation_magnitude': 0.20,
        'irreversibility': 0.10       # Decreased importance
    },
    'probability_weights': {
        'fragility_strength': 0.50,   # Much higher weight
        'historical_precedent': 0.25,
        'dependency_failures': 0.15,
        'time_horizon': 0.10
    }
}

engine = ScoringEngine(**custom_weights)
```

```bash
# Via API
curl -X POST http://localhost:8000/api/scoring/compute \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "counterfactual_ids": ["..."],
    "weights": {
      "severity_weights": {
        "cascade_depth": 0.40,
        "breadth_of_impact": 0.30,
        "deviation_magnitude": 0.20,
        "irreversibility": 0.10
      }
    }
  }'
```

### React Environment Variables

Create `frontend/react-app/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 📁 File Structure

```
Sprint 4.5 Files:

backend/
├── services/
│   └── scoring_engine.py          # Scoring algorithms
├── models/
│   └── scoring.py                 # Database models
├── schemas/
│   └── scoring.py                 # API schemas
├── api/
│   └── scoring.py                 # API endpoints
└── alembic/versions/
    └── 005_add_scoring_tables.py  # Migration

frontend/react-app/
├── src/
│   ├── components/
│   │   ├── NetworkGraph/          # D3.js graph
│   │   ├── Dashboard/             # Heat maps
│   │   ├── Comparison/            # Scenario comparison
│   │   └── Calibration/           # Expert calibration
│   ├── stores/
│   │   └── graphStore.ts          # Zustand state
│   └── App.tsx                    # Main app
├── package.json
└── vite.config.ts
```

---

## 🐛 Troubleshooting

### Backend Issues

**Error: `ModuleNotFoundError: No module named 'numpy'`**
```bash
pip install numpy scipy
```

**Error: `alembic.util.exc.CommandError: Can't locate revision identified by '004'`**
```bash
# Check existing migrations
alembic current
alembic history

# If needed, stamp to latest
alembic stamp head
```

**Error: `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: database "structured_reasoning" does not exist`**
```bash
createdb structured_reasoning
alembic upgrade head
```

### Frontend Issues

**Error: `Cannot find module 'd3' or its corresponding type declarations`**
```bash
cd frontend/react-app
npm install d3 @types/d3
```

**Error: `Failed to resolve import "@tanstack/react-query"`**
```bash
npm install @tanstack/react-query zustand react-router-dom
```

**CORS Error in Browser Console**
```python
# In backend/utils/config.py, ensure CORS_ORIGINS includes frontend
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5000",
    "http://localhost:3000"
]
```

---

## 🧪 Development Workflow

### 1. Backend Development

```bash
# Terminal 1: Backend with hot reload
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Watch logs
tail -f logs/app.log
```

### 2. Frontend Development

```bash
# Terminal 3: React dev server
cd frontend/react-app
npm run dev

# Vite provides instant HMR (Hot Module Replacement)
```

### 3. Database Inspection

```bash
# Terminal 4: PostgreSQL CLI
psql structured_reasoning

# View scores
SELECT counterfactual_id, severity_score, probability_score, risk_score
FROM counterfactual_scores
ORDER BY risk_score DESC;

# View calibration history
SELECT cf.id, sa.original_severity, sa.adjusted_severity, sa.severity_delta
FROM scoring_adjustments sa
JOIN counterfactual_scores cs ON sa.score_id = cs.id
JOIN counterfactuals cf ON cs.counterfactual_id = cf.id;
```

---

## 📚 API Documentation

### Scoring Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scoring/compute` | POST | Compute scores for counterfactuals |
| `/api/scoring/{id}` | GET | Retrieve score by counterfactual ID |
| `/api/scoring/calibrate/{id}` | PUT | Adjust score with expert judgment |
| `/api/scoring/sensitivity/{id}` | GET | Get factor sensitivity analysis |
| `/api/scoring/monte-carlo` | POST | Run risk simulation |
| `/api/scoring/calibration/statistics` | GET | Get calibration learning stats |
| `/api/scoring/status/batch` | GET | Check batch scoring progress |

### Authentication

All endpoints require JWT authentication:

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/scoring/...
```

---

## 🎯 Next Steps

### Immediate Tasks

1. **Connect React to Backend**
   - Replace sample data with API calls
   - Add authentication to frontend
   - Implement error handling

2. **Complete Heat Maps**
   - Integrate Recharts library
   - Connect to scoring API
   - Add drill-down filtering

3. **Add Testing**
   - Write unit tests for scoring engine
   - Create integration tests for API
   - Add React component tests

### Future Enhancements

1. **Phase 2-3 Pipeline**: Automated counterfactual generation
2. **WebSocket Notifications**: Real-time score updates
3. **Export Functionality**: PDF/CSV reports
4. **Performance Optimization**: Web Workers, caching
5. **Mobile Responsiveness**: Improved tablet/phone layouts

---

## 📖 Additional Resources

- **Full Documentation**: See `SPRINT_4.5_COMPLETION.md`
- **Sprint Plan**: See `SPRINT_4.5_PLAN.md`
- **API Docs**: http://localhost:8000/docs (when server running)
- **Project README**: `README.md`

---

## ✅ Verification Checklist

After completing setup, verify:

- [ ] Backend server running on port 8000
- [ ] React server running on port 5173
- [ ] Can access API documentation at `/docs`
- [ ] Can login and receive JWT token
- [ ] Can compute scores via API
- [ ] Can view network graph in browser
- [ ] Can navigate between React routes
- [ ] Database migration successful (tables exist)
- [ ] No console errors in browser
- [ ] API proxy working (no CORS errors)

---

**Questions or Issues?**

Check:
1. `SPRINT_4.5_COMPLETION.md` - Detailed technical documentation
2. API documentation - http://localhost:8000/docs
3. Browser console - For frontend errors
4. Backend logs - For API errors

**Ready to continue development!** 🚀
