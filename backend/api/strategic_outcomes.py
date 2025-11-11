"""
Phase 5: Strategic Outcomes API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from models.database import get_db
from models.user import User
from models.scenario import Scenario, Counterfactual, StrategicOutcome
from schemas.scenario import StrategicOutcomeResponse
from utils.auth import get_current_user
from services.reasoning_engine import ReasoningEngine

router = APIRouter()


@router.post("/{counterfactual_id}/outcomes", response_model=StrategicOutcomeResponse)
async def generate_strategic_outcome(
    counterfactual_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate strategic outcome trajectory (Phase 5) for a counterfactual."""
    # Verify counterfactual ownership
    counterfactual = db.query(Counterfactual).join(Scenario).filter(
        Counterfactual.id == counterfactual_id,
        Scenario.user_id == current_user.id
    ).first()

    if not counterfactual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counterfactual not found"
        )

    # Initialize reasoning engine
    reasoning_engine = ReasoningEngine()

    # Generate strategic outcome
    outcome_data = await reasoning_engine.generate_strategic_outcome(
        counterfactual.breach_condition,
        counterfactual.consequences,
        counterfactual.axis
    )

    # Store strategic outcome
    strategic_outcome = StrategicOutcome(
        counterfactual_id=counterfactual_id,
        trajectory=outcome_data["trajectory"],
        decision_points=outcome_data.get("decision_points"),
        inflection_points=outcome_data.get("inflection_points"),
        confidence_intervals=outcome_data.get("confidence_intervals")
    )
    db.add(strategic_outcome)
    db.commit()
    db.refresh(strategic_outcome)

    return strategic_outcome


@router.get("/{counterfactual_id}/outcomes", response_model=StrategicOutcomeResponse)
async def get_strategic_outcome(
    counterfactual_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get strategic outcome for a counterfactual."""
    # Verify counterfactual ownership
    counterfactual = db.query(Counterfactual).join(Scenario).filter(
        Counterfactual.id == counterfactual_id,
        Scenario.user_id == current_user.id
    ).first()

    if not counterfactual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counterfactual not found"
        )

    # Get strategic outcome
    strategic_outcome = db.query(StrategicOutcome).filter(
        StrategicOutcome.counterfactual_id == counterfactual_id
    ).first()

    if not strategic_outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategic outcome not found. Please generate it first."
        )

    return strategic_outcome
