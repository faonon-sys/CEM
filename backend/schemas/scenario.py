"""
Scenario and analysis-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


# Scenario Schemas
class ScenarioCreate(BaseModel):
    """Schema for creating a new scenario."""
    title: str = Field(..., min_length=1, max_length=255, description="Scenario title")
    description: str = Field(..., min_length=10, description="Detailed scenario description")


class ScenarioResponse(BaseModel):
    """Schema for scenario response."""
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Phase 1: Surface Analysis Schemas
class Assumption(BaseModel):
    """Schema for an individual assumption."""
    id: str
    text: str
    category: str  # political, economic, operational, etc.
    confidence: float = Field(..., ge=0.0, le=1.0)


class SurfaceAnalysisResponse(BaseModel):
    """Schema for surface analysis response."""
    id: uuid.UUID
    scenario_id: uuid.UUID
    assumptions: List[Dict[str, Any]]
    baseline_narrative: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Phase 2: Deep Questions Schemas
class QuestionDimension(BaseModel):
    """Schema for question dimension."""
    dimension: str  # temporal, structural, actor-based, resource-based, information
    description: str


class DeepQuestionResponse(BaseModel):
    """Schema for deep question response."""
    id: uuid.UUID
    surface_analysis_id: uuid.UUID
    assumption_id: str
    question_text: str
    dimension: str
    user_response: Optional[str]
    relevance_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionResponseSubmit(BaseModel):
    """Schema for submitting user response to a question."""
    user_response: str
    relevance_score: Optional[int] = Field(None, ge=1, le=5)


# Phase 3: Counterfactual Schemas
class Consequence(BaseModel):
    """Schema for a single consequence."""
    description: str
    severity: int = Field(..., ge=1, le=10)
    timeframe: str


class CounterfactualResponse(BaseModel):
    """Schema for counterfactual response."""
    id: uuid.UUID
    scenario_id: uuid.UUID
    axis: str
    breach_condition: str
    consequences: List[Dict[str, Any]]
    severity_rating: Optional[int]
    probability_rating: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# Phase 5: Strategic Outcomes Schemas
class DecisionPoint(BaseModel):
    """Schema for a decision point."""
    time: str
    description: str
    options: List[str]
    criticality: int = Field(..., ge=1, le=10)


class InflectionPoint(BaseModel):
    """Schema for an inflection point."""
    time: str
    description: str
    trajectory_change: str


class StrategicOutcomeResponse(BaseModel):
    """Schema for strategic outcome response."""
    id: uuid.UUID
    counterfactual_id: uuid.UUID
    trajectory: Dict[str, Any]
    decision_points: Optional[Dict[str, Any]]
    inflection_points: Optional[Dict[str, Any]]
    confidence_intervals: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
