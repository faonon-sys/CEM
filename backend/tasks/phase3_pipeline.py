"""
Phase 2-3 Pipeline - Automated Counterfactual Generation
Sprint 4.5 - Task 5

Orchestrates the complete flow from Phase 2 fragility analysis through
Phase 3 counterfactual generation with automatic scoring.
"""
import logging
from typing import Dict, List, Optional
from uuid import UUID
import traceback
import asyncio

from celery import Task
from celery_app import app
from sqlalchemy.orm import Session
import networkx as nx

# Import database models
from models.database import SessionLocal
from models.scenario import Scenario, Counterfactual
from models.phase3_schema import FragilityAnalysis, BreachCondition, CounterfactualV2
from models.scoring import CounterfactualScore

# Import services
from services.llm_provider import LLMProvider
from services.breach_engine import BreachConditionGenerator
from services.counterfactual_generator import CounterfactualGenerator
from services.scoring_engine import (
    ScoringEngine,
    extract_severity_factors_from_counterfactual,
    extract_probability_factors_from_counterfactual
)
from utils.config import settings

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@app.task(bind=True, base=DatabaseTask, max_retries=3, default_retry_delay=60)
def phase3_generation_pipeline(
    self,
    scenario_id: str,
    user_id: str,
    fragility_ids: Optional[List[str]] = None,
    max_breaches_per_fragility: int = 2,
    custom_scoring_weights: Optional[Dict] = None
) -> Dict:
    """
    Complete Phase 2 → Phase 3 pipeline with automatic scoring.

    Pipeline Steps:
    1. Detect Phase 2 completion and fetch results
    2. Fetch dependency graph
    3. Generate breach conditions for each fragility
    4. Generate counterfactuals for each breach
    5. Score each counterfactual (severity & probability)
    6. Store results in database
    7. Trigger frontend refresh notification

    Args:
        scenario_id: UUID of the scenario
        user_id: User ID for authorization
        fragility_ids: Optional list of specific fragility IDs (default: all)
        max_breaches_per_fragility: Max breach conditions per fragility (default: 2)
        custom_scoring_weights: Optional custom scoring weights

    Returns:
        Dictionary with pipeline results and statistics
    """
    try:
        # Step 1: Validate Phase 2 data
        self.update_state(
            state='VALIDATING',
            meta={'step': 1, 'total': 7, 'message': 'Validating Phase 2 data...'}
        )

        db = self.db
        scenario = db.query(Scenario).filter(
            Scenario.id == UUID(scenario_id)
        ).first()

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Verify ownership
        if str(scenario.user_id) != user_id:
            raise PermissionError(f"User {user_id} does not have access to this scenario")

        # Get fragility analyses
        query = db.query(FragilityAnalysis).filter(
            FragilityAnalysis.scenario_id == UUID(scenario_id)
        )

        if fragility_ids:
            query = query.filter(FragilityAnalysis.id.in_([UUID(fid) for fid in fragility_ids]))

        fragilities = query.all()

        if not fragilities:
            raise ValueError(f"No fragilities found for scenario {scenario_id}")

        logger.info(f"✓ Found {len(fragilities)} fragilities to process")

        # Step 2: Fetch Phase 2 dependency graph
        self.update_state(
            state='LOADING_DEPENDENCIES',
            meta={'step': 2, 'total': 7, 'message': 'Building dependency graph...'}
        )

        # Build NetworkX graph from Phase 2 results
        phase2_graph = nx.DiGraph()

        for fragility in fragilities:
            # Add fragility node
            phase2_graph.add_node(
                str(fragility.id),
                type='fragility',
                description=fragility.hidden_dependency,
                evidence_strength=fragility.evidence_strength,
                domains=fragility.affected_domains or [],
                actors=fragility.key_actors or [],
                resources=[]
            )

            # Add edges for related assumptions
            if fragility.related_assumption_ids:
                for assumption_id in fragility.related_assumption_ids:
                    phase2_graph.add_edge(
                        assumption_id,
                        str(fragility.id),
                        type='dependency',
                        weight=0.7
                    )

        logger.info(f"✓ Built dependency graph: {phase2_graph.number_of_nodes()} nodes, {phase2_graph.number_of_edges()} edges")

        # Step 3: Generate breach conditions
        self.update_state(
            state='GENERATING_BREACHES',
            meta={'step': 3, 'total': 7, 'message': f'Generating breach conditions for {len(fragilities)} fragilities...'}
        )

        llm_provider = LLMProvider(
            provider=settings.LLM_PROVIDER,
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY
        )

        breach_generator = BreachConditionGenerator(llm_provider)
        all_breaches = {}

        # Use asyncio to generate breaches concurrently
        loop = asyncio.get_event_loop()

        async def generate_all_breaches():
            tasks = []
            for fragility in fragilities:
                fragility_data = {
                    "id": str(fragility.id),
                    "hidden_dependency": fragility.hidden_dependency,
                    "evidence": fragility.evidence_items or [],
                    "indicators": fragility.failure_indicators or []
                }
                task = breach_generator.generate_breaches(
                    fragility_data,
                    max_count=max_breaches_per_fragility
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            breaches_dict = {}
            for fragility, result in zip(fragilities, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate breaches for {fragility.id}: {result}")
                    breaches_dict[str(fragility.id)] = []
                else:
                    breaches_dict[str(fragility.id)] = result

            return breaches_dict

        all_breaches = loop.run_until_complete(generate_all_breaches())

        total_breaches = sum(len(breaches) for breaches in all_breaches.values())
        logger.info(f"✓ Generated {total_breaches} breach conditions")

        # Store breach conditions
        breach_models = []
        for fragility_id, breaches in all_breaches.items():
            for breach_data in breaches:
                breach = BreachCondition(
                    fragility_id=UUID(fragility_id),
                    scenario_id=UUID(scenario_id),
                    axis_id=breach_data.get("axis_id"),
                    trigger_event=breach_data.get("trigger_event"),
                    conditions_required=breach_data.get("conditions_required", []),
                    indicators=breach_data.get("indicators", []),
                    time_horizon=breach_data.get("time_horizon"),
                    plausibility_score=breach_data.get("plausibility_score", 0.5)
                )
                db.add(breach)
                breach_models.append(breach)

        db.commit()
        for breach in breach_models:
            db.refresh(breach)

        # Step 4: Generate counterfactuals
        self.update_state(
            state='GENERATING_COUNTERFACTUALS',
            meta={'step': 4, 'total': 7, 'message': f'Generating counterfactuals for {len(breach_models)} breaches...'}
        )

        cf_generator = CounterfactualGenerator(llm_provider)

        async def generate_all_counterfactuals():
            tasks = []
            for breach in breach_models:
                breach_dict = {
                    "id": str(breach.id),
                    "fragility_id": str(breach.fragility_id),
                    "axis_id": breach.axis_id,
                    "trigger_event": breach.trigger_event,
                    "description": breach.trigger_event,
                    "plausibility_score": breach.plausibility_score
                }

                scenario_context = {
                    "id": scenario_id,
                    "description": scenario.description
                }

                task = cf_generator.generate_counterfactual(
                    breach_condition=breach_dict,
                    phase2_graph=phase2_graph,
                    scenario_context=scenario_context
                )
                tasks.append((breach, task))

            results = []
            for breach, task in tasks:
                try:
                    result = await task
                    results.append((breach, result))
                except Exception as e:
                    logger.error(f"Failed to generate counterfactual for breach {breach.id}: {e}")
                    results.append((breach, None))

            return results

        cf_results = loop.run_until_complete(generate_all_counterfactuals())

        # Store counterfactuals
        counterfactual_models = []
        for breach, cf_data in cf_results:
            if cf_data is None:
                continue

            counterfactual = CounterfactualV2(
                breach_id=breach.id,
                scenario_id=UUID(scenario_id),
                axis_id=cf_data.get("axis"),
                breach_condition=breach.trigger_event,
                narrative=cf_data.get("narrative"),
                divergence_timeline=cf_data.get("divergence_timeline", []),
                consequence_chain=cf_data.get("consequences", []),
                affected_domains=cf_data.get("affected_domains", []),
                time_horizon=breach.time_horizon,
                preliminary_severity=cf_data.get("preliminary_severity", 0.5),
                preliminary_probability=cf_data.get("preliminary_probability", 0.5)
            )
            db.add(counterfactual)
            counterfactual_models.append((counterfactual, cf_data))

        db.commit()
        for counterfactual, _ in counterfactual_models:
            db.refresh(counterfactual)

        logger.info(f"✓ Generated {len(counterfactual_models)} counterfactuals")

        # Step 5: Score counterfactuals
        self.update_state(
            state='SCORING',
            meta={'step': 5, 'total': 7, 'message': f'Scoring {len(counterfactual_models)} counterfactuals...'}
        )

        # Initialize scoring engine with custom weights if provided
        if custom_scoring_weights:
            scoring_engine = ScoringEngine(
                severity_weights=custom_scoring_weights.get('severity'),
                probability_weights=custom_scoring_weights.get('probability')
            )
        else:
            scoring_engine = ScoringEngine()

        score_models = []
        for counterfactual, cf_data in counterfactual_models:
            try:
                # Prepare data for factor extraction
                cf_full_data = {
                    "consequences": cf_data.get("consequences", []),
                    "estimated_severity": cf_data.get("preliminary_severity", 0.5),
                    "fragility_evidence_score": cf_data.get("preliminary_probability", 0.5),
                    "description": cf_data.get("narrative", ""),
                    "time_horizon": cf_data.get("time_horizon", "medium"),
                    "breach_conditions": cf_data.get("divergence_timeline", []),
                    "historical_precedent": False,
                    "precedent_count": 0
                }

                # Extract factors and calculate scores
                severity_factors = extract_severity_factors_from_counterfactual(cf_full_data)
                probability_factors = extract_probability_factors_from_counterfactual(cf_full_data)

                severity_result = scoring_engine.calculate_severity(severity_factors)
                probability_result = scoring_engine.calculate_probability(probability_factors)

                # Store score
                score = CounterfactualScore(
                    counterfactual_id=counterfactual.id,
                    severity_score=severity_result.score,
                    severity_confidence_lower=severity_result.confidence_interval[0],
                    severity_confidence_upper=severity_result.confidence_interval[1],
                    severity_factors=severity_result.factors,
                    severity_sensitivity=severity_result.sensitivity,
                    probability_score=probability_result.score,
                    probability_confidence_lower=probability_result.confidence_interval[0],
                    probability_confidence_upper=probability_result.confidence_interval[1],
                    probability_factors=probability_result.factors,
                    probability_sensitivity=probability_result.sensitivity,
                    risk_score=severity_result.score * probability_result.score,
                    scoring_version="1.0",
                    is_expert_adjusted=False
                )
                db.add(score)
                score_models.append(score)

            except Exception as e:
                logger.error(f"Failed to score counterfactual {counterfactual.id}: {e}")
                continue

        db.commit()
        logger.info(f"✓ Scored {len(score_models)} counterfactuals")

        # Step 6: Persist results
        self.update_state(
            state='PERSISTING',
            meta={'step': 6, 'total': 7, 'message': 'Persisting results...'}
        )

        # Already committed above, just log summary
        logger.info(f"✓ Pipeline results persisted to database")

        # Step 7: Complete (trigger frontend refresh would go here)
        self.update_state(
            state='SUCCESS',
            meta={'step': 7, 'total': 7, 'message': 'Pipeline completed successfully'}
        )

        return {
            'status': 'completed',
            'scenario_id': scenario_id,
            'statistics': {
                'fragilities_processed': len(fragilities),
                'breaches_generated': total_breaches,
                'counterfactuals_generated': len(counterfactual_models),
                'counterfactuals_scored': len(score_models),
                'average_severity': sum(s.severity_score for s in score_models) / len(score_models) if score_models else 0,
                'average_probability': sum(s.probability_score for s in score_models) / len(score_models) if score_models else 0,
                'high_risk_count': sum(1 for s in score_models if s.risk_score > 0.7)
            },
            'counterfactual_ids': [str(cf.id) for cf, _ in counterfactual_models]
        }

    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        return {
            'status': 'failed',
            'error': 'permission_denied',
            'message': str(e)
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'status': 'failed',
            'error': 'validation_error',
            'message': str(e)
        }

    except Exception as exc:
        logger.error(f"Pipeline error: {exc}")
        logger.error(traceback.format_exc())

        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        except self.MaxRetriesExceededError:
            return {
                'status': 'failed',
                'error': 'max_retries_exceeded',
                'message': str(exc),
                'traceback': traceback.format_exc()
            }


@app.task
def check_phase3_pipeline_status(task_id: str) -> Dict:
    """
    Check status of Phase 3 pipeline.

    Args:
        task_id: Celery task ID

    Returns:
        Dictionary with task status and progress
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=app)

    response = {
        'task_id': task_id,
        'state': result.state,
        'ready': result.ready(),
        'successful': result.successful() if result.ready() else False,
        'failed': result.failed() if result.ready() else False
    }

    if result.info:
        if isinstance(result.info, dict):
            response['progress'] = result.info
        else:
            response['result'] = result.info

    return response
