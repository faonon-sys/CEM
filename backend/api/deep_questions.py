"""
Phase 2: Deep Questions API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from models.database import get_db
from models.user import User
from models.scenario import Scenario, SurfaceAnalysis, DeepQuestion
from schemas.scenario import DeepQuestionResponse, QuestionResponseSubmit
from utils.auth import get_current_user
from services.reasoning_engine import ReasoningEngine

router = APIRouter()


@router.post("/{scenario_id}/deep-questions", response_model=List[DeepQuestionResponse])
async def generate_deep_questions(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate deep probing questions (Phase 2) for a scenario."""
    # Verify scenario ownership and get surface analysis
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found. Please generate Phase 1 first."
        )

    # Initialize reasoning engine
    reasoning_engine = ReasoningEngine()

    # Generate questions
    questions = await reasoning_engine.generate_probing_questions(
        surface_analysis.assumptions
    )

    # Store questions
    question_models = []
    for question in questions:
        deep_question = DeepQuestion(
            surface_analysis_id=surface_analysis.id,
            assumption_id=question["assumption_id"],
            question_text=question["question_text"],
            dimension=question["dimension"]
        )
        db.add(deep_question)
        question_models.append(deep_question)

    db.commit()

    for q in question_models:
        db.refresh(q)

    return question_models


@router.get("/{scenario_id}/deep-questions", response_model=List[DeepQuestionResponse])
async def get_deep_questions(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all deep questions for a scenario."""
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
            detail="Surface analysis not found"
        )

    # Get questions
    questions = db.query(DeepQuestion).filter(
        DeepQuestion.surface_analysis_id == surface_analysis.id
    ).all()

    return questions


@router.post("/{scenario_id}/deep-questions/{question_id}/respond", response_model=DeepQuestionResponse)
async def respond_to_question(
    scenario_id: uuid.UUID,
    question_id: uuid.UUID,
    response_data: QuestionResponseSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit user response to a deep question."""
    # Verify ownership chain
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get question
    question = db.query(DeepQuestion).filter(DeepQuestion.id == question_id).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Update question with user response
    question.user_response = response_data.user_response
    question.relevance_score = response_data.relevance_score

    db.commit()
    db.refresh(question)

    return question
