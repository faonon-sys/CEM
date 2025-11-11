"""
Phase 2-3 Pipeline API Endpoints
Sprint 4.5 - Task 5

REST API for triggering and monitoring the automated Phase 2-3 pipeline.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import uuid

from models.database import get_db
from models.user import User
from utils.auth import get_current_user
from tasks.phase3_pipeline import phase3_generation_pipeline, check_phase3_pipeline_status

router = APIRouter(prefix="/api/v1/pipeline", tags=["Phase 3 Pipeline"])


class PipelineTriggerRequest(BaseModel):
    """Request to trigger Phase 3 pipeline"""
    scenario_id: str = Field(..., description="Scenario ID")
    fragility_ids: Optional[List[str]] = Field(None, description="Specific fragility IDs (default: all)")
    max_breaches_per_fragility: int = Field(2, description="Max breaches per fragility", ge=1, le=5)
    custom_scoring_weights: Optional[Dict] = Field(None, description="Custom scoring weights")


class PipelineTriggerResponse(BaseModel):
    """Response after triggering pipeline"""
    task_id: str
    status: str
    message: str


class PipelineStatusResponse(BaseModel):
    """Pipeline status response"""
    task_id: str
    state: str
    ready: bool
    successful: bool
    failed: bool
    progress: Optional[Dict] = None
    result: Optional[Dict] = None


@router.post("/phase3/generate", response_model=PipelineTriggerResponse)
async def trigger_phase3_pipeline(
    request: PipelineTriggerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger automated Phase 2-3 pipeline.

    This endpoint starts an async pipeline that:
    1. Fetches Phase 2 fragility analysis
    2. Generates breach conditions
    3. Generates counterfactuals
    4. Scores all counterfactuals
    5. Stores results in database

    Returns a task_id that can be used to monitor progress.
    """
    try:
        # Validate scenario_id format
        try:
            uuid.UUID(request.scenario_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scenario_id format"
            )

        # Trigger async pipeline
        task = phase3_generation_pipeline.delay(
            scenario_id=request.scenario_id,
            user_id=str(current_user.id),
            fragility_ids=request.fragility_ids,
            max_breaches_per_fragility=request.max_breaches_per_fragility,
            custom_scoring_weights=request.custom_scoring_weights
        )

        return PipelineTriggerResponse(
            task_id=task.id,
            status="started",
            message=f"Phase 3 pipeline started for scenario {request.scenario_id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger pipeline: {str(e)}"
        )


@router.get("/phase3/status/{task_id}", response_model=PipelineStatusResponse)
async def get_phase3_pipeline_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Check status of Phase 3 pipeline task.

    States:
    - PENDING: Task is queued but not started
    - VALIDATING: Validating Phase 2 data
    - LOADING_DEPENDENCIES: Building dependency graph
    - GENERATING_BREACHES: Creating breach conditions
    - GENERATING_COUNTERFACTUALS: Creating counterfactuals
    - SCORING: Calculating scores
    - PERSISTING: Saving to database
    - SUCCESS: Pipeline completed
    - FAILURE: Pipeline failed
    """
    try:
        status_data = check_phase3_pipeline_status(task_id)
        return PipelineStatusResponse(**status_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check pipeline status: {str(e)}"
        )


@router.get("/scenarios/{scenario_id}/counterfactuals")
async def get_scenario_counterfactuals(
    scenario_id: str,
    include_scores: bool = True,
    min_severity: Optional[float] = None,
    min_probability: Optional[float] = None,
    axis_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all counterfactuals for a scenario with optional filtering.

    Supports filtering by:
    - min_severity: Minimum severity score (0-1)
    - min_probability: Minimum probability score (0-1)
    - axis_filter: Specific axis ID
    """
    from models.phase3_schema import CounterfactualV2
    from models.scoring import CounterfactualScore

    try:
        scenario_uuid = uuid.UUID(scenario_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scenario_id format"
        )

    # Build query
    query = db.query(CounterfactualV2).filter(
        CounterfactualV2.scenario_id == scenario_uuid
    )

    if axis_filter:
        query = query.filter(CounterfactualV2.axis_id == axis_filter)

    counterfactuals = query.all()

    # Add scores and apply score filters
    results = []
    for cf in counterfactuals:
        cf_dict = {
            "id": str(cf.id),
            "breach_id": str(cf.breach_id),
            "scenario_id": str(cf.scenario_id),
            "axis_id": cf.axis_id,
            "breach_condition": cf.breach_condition,
            "narrative": cf.narrative,
            "divergence_timeline": cf.divergence_timeline,
            "consequence_chain": cf.consequence_chain,
            "affected_domains": cf.affected_domains,
            "time_horizon": cf.time_horizon,
            "created_at": cf.created_at.isoformat() if cf.created_at else None
        }

        if include_scores:
            score = db.query(CounterfactualScore).filter(
                CounterfactualScore.counterfactual_id == cf.id
            ).first()

            if score:
                cf_dict["scores"] = {
                    "severity": score.severity_score,
                    "severity_ci": [score.severity_confidence_lower, score.severity_confidence_upper],
                    "probability": score.probability_score,
                    "probability_ci": [score.probability_confidence_lower, score.probability_confidence_upper],
                    "risk": score.risk_score,
                    "is_expert_adjusted": score.is_expert_adjusted
                }

                # Apply score filters
                if min_severity and score.severity_score < min_severity:
                    continue
                if min_probability and score.probability_score < min_probability:
                    continue
            else:
                cf_dict["scores"] = None

        results.append(cf_dict)

    return {
        "scenario_id": scenario_id,
        "counterfactuals": results,
        "total": len(results)
    }


@router.get("/scenarios/{scenario_id}/graph")
async def get_scenario_graph(
    scenario_id: str,
    include_scores: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get graph representation of scenario for network visualization.

    Returns nodes (assumptions, fragilities, breaches, counterfactuals)
    and edges (dependencies, consequences, transitions).
    """
    from models.phase3_schema import FragilityAnalysis, BreachCondition, CounterfactualV2
    from models.scoring import CounterfactualScore

    try:
        scenario_uuid = uuid.UUID(scenario_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scenario_id format"
        )

    # Get all entities
    fragilities = db.query(FragilityAnalysis).filter(
        FragilityAnalysis.scenario_id == scenario_uuid
    ).all()

    breaches = db.query(BreachCondition).filter(
        BreachCondition.scenario_id == scenario_uuid
    ).all()

    counterfactuals = db.query(CounterfactualV2).filter(
        CounterfactualV2.scenario_id == scenario_uuid
    ).all()

    # Build nodes
    nodes = []
    edges = []

    # Fragility nodes
    for frag in fragilities:
        nodes.append({
            "id": str(frag.id),
            "type": "fragility",
            "label": frag.hidden_dependency[:50] + "..." if len(frag.hidden_dependency) > 50 else frag.hidden_dependency,
            "metadata": {
                "evidence_strength": frag.evidence_strength,
                "affected_domains": frag.affected_domains
            }
        })

    # Breach nodes
    for breach in breaches:
        nodes.append({
            "id": str(breach.id),
            "type": "breach",
            "label": breach.trigger_event[:50] + "..." if len(breach.trigger_event) > 50 else breach.trigger_event,
            "metadata": {
                "axis_id": breach.axis_id,
                "time_horizon": breach.time_horizon,
                "plausibility": breach.plausibility_score
            }
        })

        # Edge from fragility to breach
        edges.append({
            "source": str(breach.fragility_id),
            "target": str(breach.id),
            "type": "transition",
            "weight": breach.plausibility_score or 0.5
        })

    # Counterfactual nodes
    for cf in counterfactuals:
        score = None
        if include_scores:
            score = db.query(CounterfactualScore).filter(
                CounterfactualScore.counterfactual_id == cf.id
            ).first()

        nodes.append({
            "id": str(cf.id),
            "type": "counterfactual",
            "label": cf.narrative[:50] + "..." if len(cf.narrative) > 50 else cf.narrative,
            "severity": score.severity_score if score else cf.preliminary_severity,
            "probability": score.probability_score if score else cf.preliminary_probability,
            "metadata": {
                "axis_id": cf.axis_id,
                "affected_domains": cf.affected_domains,
                "time_horizon": cf.time_horizon
            }
        })

        # Edge from breach to counterfactual
        edges.append({
            "source": str(cf.breach_id),
            "target": str(cf.id),
            "type": "consequence",
            "weight": score.probability_score if score else 0.5
        })

    return {
        "scenario_id": scenario_id,
        "nodes": nodes,
        "edges": edges,
        "statistics": {
            "fragilities": len(fragilities),
            "breaches": len(breaches),
            "counterfactuals": len(counterfactuals),
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    }
