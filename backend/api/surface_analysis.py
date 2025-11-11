"""
Phase 1: Surface Analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from models.database import get_db
from models.user import User
from models.scenario import Scenario, SurfaceAnalysis
from schemas.scenario import SurfaceAnalysisResponse
from utils.auth import get_current_user
from services.reasoning_engine import ReasoningEngine

router = APIRouter()


@router.post("/{scenario_id}/surface-analysis", response_model=SurfaceAnalysisResponse)
async def create_surface_analysis(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate surface analysis (Phase 1) for a scenario."""
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

    # Initialize reasoning engine
    reasoning_engine = ReasoningEngine()

    # Extract assumptions
    assumptions = await reasoning_engine.extract_assumptions(scenario.description)

    # Generate baseline narrative
    baseline_narrative = await reasoning_engine.generate_baseline_narrative(
        scenario.description,
        assumptions
    )

    # Store surface analysis
    surface_analysis = SurfaceAnalysis(
        scenario_id=scenario_id,
        assumptions=assumptions,
        baseline_narrative=baseline_narrative
    )
    db.add(surface_analysis)
    db.commit()
    db.refresh(surface_analysis)

    return surface_analysis


@router.get("/{scenario_id}/surface-analysis", response_model=SurfaceAnalysisResponse)
async def get_surface_analysis(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get surface analysis for a scenario."""
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

    # Get surface analysis
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found. Please generate it first."
        )

    return surface_analysis
