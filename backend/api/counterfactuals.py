"""
Phase 3: Counterfactual Generation API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from models.database import get_db
from models.user import User
from models.scenario import Scenario, SurfaceAnalysis, DeepQuestion, Counterfactual
from schemas.scenario import CounterfactualResponse
from utils.auth import get_current_user
from services.reasoning_engine import ReasoningEngine

router = APIRouter()


@router.post("/{scenario_id}/counterfactuals", response_model=List[CounterfactualResponse])
async def generate_counterfactuals(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate counterfactual scenarios (Phase 3) across six strategic axes."""
    # Verify scenario ownership
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get surface analysis and questions
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found. Please generate Phase 1 first."
        )

    deep_questions = db.query(DeepQuestion).filter(
        DeepQuestion.surface_analysis_id == surface_analysis.id
    ).all()

    # Initialize reasoning engine
    reasoning_engine = ReasoningEngine()

    # Generate counterfactuals
    counterfactuals_data = await reasoning_engine.generate_counterfactuals(
        scenario.description,
        surface_analysis.assumptions,
        [{"question_text": q.question_text, "dimension": q.dimension} for q in deep_questions]
    )

    # Store counterfactuals
    counterfactual_models = []
    for cf_data in counterfactuals_data:
        counterfactual = Counterfactual(
            scenario_id=scenario_id,
            axis=cf_data["axis"],
            breach_condition=cf_data["breach_condition"],
            consequences=cf_data["consequences"],
            severity_rating=cf_data.get("severity_rating"),
            probability_rating=cf_data.get("probability_rating")
        )
        db.add(counterfactual)
        counterfactual_models.append(counterfactual)

    db.commit()

    for cf in counterfactual_models:
        db.refresh(cf)

    return counterfactual_models


@router.get("/{scenario_id}/counterfactuals", response_model=List[CounterfactualResponse])
async def get_counterfactuals(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all counterfactuals for a scenario."""
    # Verify scenario ownership
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get counterfactuals
    counterfactuals = db.query(Counterfactual).filter(
        Counterfactual.scenario_id == scenario_id
    ).all()

    return counterfactuals
