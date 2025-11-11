# Structured Reasoning System

A multi-phase analytical framework for deconstructing complex, high-stakes scenarios through systematic reasoning.

## Overview

This system provides a structured approach to analyzing complex scenarios through five distinct phases:

1. **Surface Premise Analysis** - Identifies dominant assumptions and baseline narratives
2. **Deep Questioning** - Exposes hidden fragilities and unstated dependencies
3. **Counterfactual Generation** - Explores alternative outcomes across six strategic axes
4. **Strategic Outcome Projection** - Maps trajectory pathways and decision points

## Technology Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL 15+** with JSONB support
- **SQLAlchemy** ORM with Alembic migrations
- **Anthropic Claude 3.5 Sonnet** for LLM reasoning

### Frontend
- **Streamlit** for rapid prototyping and UI
- **TypeScript** (future migration path to React)

### Infrastructure
- **Docker** & docker-compose
- **Redis** for async processing
- **GitHub Actions** for CI/CD

## Project Structure

```
structured-reasoning/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── services/         # LLM, reasoning engines
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── utils/            # Prompt templates, helpers
│   └── main.py           # Application entry point
├── frontend/
│   ├── streamlit_app/    # Streamlit UI pages
│   ├── components/       # Reusable UI components
│   └── services/         # API clients
├── tests/
│   ├── unit/
│   ├── integration/
│   └── golden_dataset/   # Test scenarios
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)
- Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd test
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Start services with Docker:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
cd backend
alembic upgrade head
```

5. Start the development server:
```bash
# Backend API
cd backend
uvicorn main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
streamlit run streamlit_app/main.py --server.port 5000
```

6. Access the application:
- Frontend UI: http://localhost:5000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test suite
pytest tests/unit/
pytest tests/integration/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black backend/ frontend/

# Lint
flake8 backend/
pylint backend/

# Type checking
mypy backend/
```

## Architecture

### System Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  (Streamlit)│     │   Backend    │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ LLM Provider │
                    │ (Anthropic)  │
                    └──────────────┘
```

### Analysis Workflow

1. **User Input** → Scenario description
2. **Phase 1** → Extract assumptions and baseline narrative
3. **Phase 2** → Generate probing questions across multiple dimensions
4. **Phase 3** → Create counterfactual scenarios across six axes
5. **Phase 5** → Project strategic outcome trajectories
6. **Export** → Generate comprehensive analysis report

## Phase Descriptions

### Phase 1: Surface Premise Analysis
Identifies and categorizes dominant assumptions underlying the scenario. Extracts baseline narrative and conventional wisdom that will be challenged in subsequent phases.

### Phase 2: Deep Questioning
Systematically interrogates each assumption across five dimensions:
- Temporal: Timeline compression/extension
- Structural: Load-bearing dependencies
- Actor-based: Incentive shifts
- Resource-based: Constraint bindings
- Information: Unknown unknowns

### Phase 3: Counterfactual Generation
Explores alternative outcomes across six strategic axes:
1. Geopolitical alignment shifts
2. Economic constraint breaches
3. Technological disruption
4. Actor strategy changes
5. Information environment shifts
6. Resource availability changes

### Phase 5: Strategic Outcomes
Projects trajectory pathways over time horizons (T+1mo, T+3mo, T+6mo, T+1yr), identifying critical decision points, inflection points, and confidence intervals.

## API Documentation

### Core Endpoints

#### Scenarios
- `POST /api/scenarios` - Create new scenario
- `GET /api/scenarios/{id}` - Retrieve scenario
- `GET /api/scenarios` - List user scenarios

#### Phase 1: Surface Analysis
- `POST /api/scenarios/{id}/surface-analysis` - Extract assumptions
- `GET /api/scenarios/{id}/surface-analysis` - Get assumptions

#### Phase 2: Deep Questions
- `POST /api/scenarios/{id}/deep-questions` - Generate questions
- `POST /api/scenarios/{id}/deep-questions/{question_id}/respond` - Submit response

#### Phase 3: Counterfactuals
- `POST /api/scenarios/{id}/counterfactuals` - Generate counterfactuals
- `GET /api/scenarios/{id}/counterfactuals` - List counterfactuals

#### Phase 5: Strategic Outcomes
- `POST /api/counterfactuals/{id}/outcomes` - Project trajectories
- `GET /api/counterfactuals/{id}/outcomes` - Retrieve outcomes

## Configuration

### Environment Variables

```bash
# API Configuration
ANTHROPIC_API_KEY=your_api_key_here
OPENAI_API_KEY=your_fallback_key_here
LLM_PROVIDER=anthropic  # or openai

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/reasoning_db

# Redis
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Feature Flags
PHASE_1_ENABLED=true
PHASE_2_ENABLED=true
PHASE_3_ENABLED=true
PHASE_5_ENABLED=true

# Server
BACKEND_PORT=8000
FRONTEND_PORT=5000
```

## Testing Strategy

### Golden Dataset
The system includes a curated set of test scenarios with human-annotated expected outputs for validation:

1. Geopolitical Crisis Scenario
2. Corporate Strategy Scenario
3. Policy Decision Scenario
4. Technology Disruption Scenario
5. Economic Shock Scenario

### Quality Metrics
- Assumption extraction relevance: >75%
- Question dimension coverage: 5/5 dimensions
- Counterfactual axis coverage: 6/6 axes
- API response time: <2s per phase

## Deployment

### Production Deployment
```bash
# Build containers
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Monitoring
- Application logs: `docker-compose logs -f`
- Database metrics: PostgreSQL monitoring
- LLM usage tracking: Token usage dashboard

## Security

### Authentication Flow
1. User registers → Password hashed with bcrypt (cost factor 12)
2. User logs in → JWT access token (1hr) + refresh token (7d)
3. Protected endpoints → Bearer token validation
4. User-scoped queries → Automatic filtering by user_id

### Security Measures
- HTTPS enforced in production
- API rate limiting (10 req/min per user)
- SQL injection prevention via ORM
- Input validation with Pydantic schemas
- Secrets management via environment variables

## Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement changes with tests
3. Run quality checks: `black`, `flake8`, `pytest`
4. Submit PR with description
5. CI pipeline validates changes
6. Code review and merge

### Code Style
- Python: PEP 8, Black formatting, type hints
- Commit messages: Conventional Commits format
- Documentation: Docstrings for all public functions

## Troubleshooting

### Common Issues

**LLM API timeouts**
- Check API key validity
- Verify rate limits not exceeded
- Switch to fallback provider if needed

**Database connection errors**
- Ensure PostgreSQL is running
- Verify DATABASE_URL in .env
- Check firewall/network settings

**Streamlit not loading**
- Clear cache: `streamlit cache clear`
- Check port 5000 availability
- Review browser console logs

## License

[License details to be added]

## Contact

[Contact information to be added]

## Acknowledgments

Built with Claude 3.5 Sonnet for advanced reasoning capabilities.
