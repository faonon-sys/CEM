# Quick Start Guide - Structured Reasoning System

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Anthropic API key

### Step 1: Get API Key
1. Sign up at https://console.anthropic.com/
2. Generate an API key
3. Keep it handy for step 3

### Step 2: Clone and Setup
```bash
cd /Users/raminhedayatpour/Documents/VibeProjects/test
chmod +x scripts/*.sh
./scripts/setup.sh
```

### Step 3: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API key
nano .env  # or use your favorite editor

# Required: Add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional: Add OpenAI as fallback
OPENAI_API_KEY=sk-...
```

### Step 4: Start the System
```bash
./scripts/run_dev.sh
```

### Step 5: Access the Application
- **Frontend UI:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🎯 First Analysis

### 1. Register/Login
- Open http://localhost:5000
- Click "Register" tab
- Create account with email/password
- Login with credentials

### 2. Create Scenario
- Navigate to "📝 Scenario Input"
- Enter title: `"Tech Company AI Launch"`
- Enter description:
  ```
  A major technology company is planning to launch a revolutionary AI
  product that could disrupt the entire industry. The company assumes
  regulatory frameworks will remain stable, competitors won't develop
  similar technology quickly, and consumer adoption will be rapid.
  Market analysts expect the product to achieve 50% market penetration
  within 18 months.
  ```
- Click "Create Scenario"

### 3. Run Phase 1: Assumptions
- Navigate to "🎯 Phase 1: Assumptions"
- Click "Generate Assumptions"
- Wait 10-15 seconds
- Review extracted assumptions

### 4. Run Phase 2: Deep Questions
- Navigate to "❓ Phase 2: Deep Questions"
- Click "Generate Probing Questions"
- Wait 15-20 seconds
- Browse questions by dimension

### 5. Run Phase 3: Counterfactuals
- Navigate to "🔀 Phase 3: Counterfactuals"
- Click "Generate Counterfactuals"
- Wait 20-30 seconds
- Explore scenarios across 6 axes

### 6. Run Phase 5: Strategic Outcomes
- Navigate to "📊 Phase 5: Strategic Outcomes"
- Select a counterfactual from dropdown
- Click "Generate Strategic Outcome"
- Wait 15-20 seconds
- Review trajectory timeline

---

## 🔧 Troubleshooting

### Issue: "Failed to connect to backend"
**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, restart:
cd backend
uvicorn main:app --reload --port 8000
```

### Issue: "LLM API error"
**Solution:**
1. Check your API key in `.env`
2. Verify you have API credits
3. Check rate limits (wait a minute)

### Issue: "Database connection error"
**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not, start it:
docker-compose up -d postgres
```

### Issue: "Port already in use"
**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --reload --port 8001
```

---

## 📖 Key Concepts

### Phase 1: Surface Premise Analysis
- **What:** Extracts underlying assumptions from scenario
- **Output:** 5-15 assumptions with categories and confidence scores
- **Time:** ~15 seconds

### Phase 2: Deep Questioning
- **What:** Challenges assumptions across 5 dimensions
- **Output:** 20-30 probing questions
- **Dimensions:** Temporal, Structural, Actor-based, Resource-based, Information
- **Time:** ~20 seconds

### Phase 3: Counterfactual Generation
- **What:** Explores alternative outcomes when assumptions break
- **Output:** 18-30 scenarios across 6 axes
- **Axes:** Geopolitical, Economic, Technological, Actor Strategy, Information, Resources
- **Time:** ~30 seconds

### Phase 5: Strategic Outcomes
- **What:** Projects trajectory over time with decision points
- **Output:** Timeline (T+1mo to T+1yr) with inflection points
- **Time:** ~20 seconds

---

## 🎓 Example Scenarios

### Geopolitical Crisis
```
Title: "Taiwan Strait Military Standoff"
Description: A military standoff in the Taiwan Strait has escalated
following aggressive Chinese exercises and U.S. naval deployments.
Key assumptions include both sides seeking to avoid confrontation,
allies maintaining positions, and economic ties serving as deterrent.
```

### Corporate Strategy
```
Title: "Major Acquisition During Market Downturn"
Description: A Fortune 500 company is pursuing a $10B acquisition
of a struggling competitor during economic uncertainty. Assumes
regulatory approval, integration success, and market recovery
within 24 months.
```

### Climate Policy
```
Title: "Global Carbon Pricing Agreement"
Description: International negotiations toward unified carbon pricing
face deadlines. Assumes major economies will participate, enforcement
mechanisms will work, and economic impacts will be manageable through
gradual implementation.
```

---

## 📚 API Usage (Advanced)

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Returns: {"access_token":"...","token_type":"bearer"}
```

### Create Scenario
```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/scenarios/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Test Scenario",
    "description":"A test scenario for API exploration"
  }'
```

### Generate Phase 1 Analysis
```bash
SCENARIO_ID="your_scenario_id_here"

curl -X POST http://localhost:8000/api/scenarios/$SCENARIO_ID/surface-analysis \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🛠️ Development Tips

### View Logs
```bash
# Backend logs
cd backend
tail -f logs/app.log

# Frontend logs (in terminal running streamlit)

# Database logs
docker logs reasoning_postgres
```

### Database Access
```bash
# Connect to database
docker exec -it reasoning_postgres psql -U reasoning_user -d reasoning_db

# Useful queries:
SELECT * FROM users;
SELECT id, title FROM scenarios;
SELECT COUNT(*) FROM surface_analyses;
```

### Test LLM Connection
```python
# In backend directory
python3
>>> from services.llm_provider import get_llm_provider
>>> import asyncio
>>> provider = get_llm_provider()
>>> result = asyncio.run(provider.complete("Say hello"))
>>> print(result['content'])
```

---

## 🎯 Next Steps

1. **Try Different Scenarios:** Test with various domains (tech, geopolitics, policy)
2. **Explore API Docs:** Visit http://localhost:8000/docs for interactive API testing
3. **Review Code:** Check `backend/services/reasoning_engine.py` for phase logic
4. **Customize Prompts:** Edit `backend/utils/prompts.py` to adjust LLM behavior
5. **Add Features:** Extend with PDF export, comparison views, etc.

---

## 📞 Support

- **Documentation:** See README.md and SPRINT_1_COMPLETION.md
- **API Reference:** http://localhost:8000/docs
- **Issues:** Check logs in `logs/` directory
- **Code Structure:** See architecture diagram in SPRINT_1_COMPLETION.md

---

## 🎉 Success Criteria

You're ready when you can:
- [x] Register and login
- [x] Create a scenario
- [x] Generate Phase 1 assumptions
- [x] Generate Phase 2 questions
- [x] Generate Phase 3 counterfactuals
- [x] Generate Phase 5 outcomes
- [x] Navigate between phases smoothly
- [x] View all results in UI

Happy analyzing! 🧠
