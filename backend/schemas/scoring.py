"""
Pydantic schemas for scoring API requests and responses.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from uuid import UUID


class SeverityFactorsSchema(BaseModel):
    """Severity factors for scoring."""
    cascade_depth: float = Field(..., ge=0, le=1, description="Consequence chain depth (0-1)")
    breadth_of_impact: float = Field(..., ge=0, le=1, description="Number of domains affected (0-1)")
    deviation_magnitude: float = Field(..., ge=0, le=1, description="Distance from baseline (0-1)")
    irreversibility: float = Field(..., ge=0, le=1, description="Difficulty to reverse (0-1)")


class ProbabilityFactorsSchema(BaseModel):
    """Probability factors for scoring."""
    fragility_strength: float = Field(..., ge=0, le=1, description="Evidence strength (0-1)")
    historical_precedent: float = Field(..., ge=0, le=1, description="Past event frequency (0-1)")
    dependency_failures: float = Field(..., ge=0, le=1, description="Required failures (0-1)")
    time_horizon: float = Field(..., ge=0, le=1, description="Time distance adjustment (0-1)")


class ScoreWeightsSchema(BaseModel):
    """Custom weights for scoring factors."""
    severity_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom severity factor weights (must sum to 1.0)"
    )
    probability_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom probability factor weights (must sum to 1.0)"
    )

    @validator('severity_weights', 'probability_weights')
    def validate_weights_sum(cls, v):
        """Ensure weights sum to 1.0."""
        if v is not None:
            total = sum(v.values())
            if not 0.99 <= total <= 1.01:
                raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v


class ComputeScoresRequest(BaseModel):
    """Request to compute scores for counterfactuals."""
    counterfactual_ids: List[UUID] = Field(..., description="List of counterfactual IDs to score")
    weights: Optional[ScoreWeightsSchema] = Field(default=None, description="Optional custom weights")
    force_recompute: bool = Field(default=False, description="Recompute even if scores exist")


class ScoreResultSchema(BaseModel):
    """Individual score result."""
    score: float = Field(..., description="Final score (0-1)")
    confidence_interval: Tuple[float, float] = Field(..., description="95% confidence interval")
    factors: Dict[str, float] = Field(..., description="Individual factor contributions")
    sensitivity: Dict[str, float] = Field(..., description="Factor influence scores")


class CounterfactualScoreResponse(BaseModel):
    """Response for a single counterfactual score."""
    id: UUID
    counterfactual_id: UUID
    severity: ScoreResultSchema
    probability: ScoreResultSchema
    risk_score: Optional[float] = Field(None, description="severity × probability")
    calibration: Optional[Dict] = None
    metadata: Dict


class ComputeScoresResponse(BaseModel):
    """Response containing computed scores."""
    scores: List[CounterfactualScoreResponse]
    computation_time: float = Field(..., description="Computation time in seconds")
    message: str


class CalibrateScoreRequest(BaseModel):
    """Request to calibrate (adjust) a score."""
    severity_adjustment: float = Field(..., ge=0, le=1, description="Expert-adjusted severity score")
    probability_adjustment: float = Field(..., ge=0, le=1, description="Expert-adjusted probability score")
    rationale: Optional[str] = Field(None, description="Explanation for adjustment")


class CalibrateScoreResponse(BaseModel):
    """Response after calibrating a score."""
    score_id: UUID
    updated_score: CounterfactualScoreResponse
    adjustment_delta: Dict[str, float]
    message: str


class SensitivityAnalysisResponse(BaseModel):
    """Response for sensitivity analysis."""
    counterfactual_id: UUID
    severity_sensitivity: Dict[str, float]
    probability_sensitivity: Dict[str, float]
    most_influential_factors: Dict[str, str]
    message: str


class MonteCarloSimulationRequest(BaseModel):
    """Request to run Monte Carlo simulation."""
    counterfactual_id: UUID
    n_simulations: int = Field(default=10000, ge=1000, le=100000, description="Number of simulation runs")


class MonteCarloSimulationResponse(BaseModel):
    """Response from Monte Carlo simulation."""
    counterfactual_id: UUID
    severity: Dict
    probability: Dict
    risk: Dict
    message: str


class CalibrationStatisticsResponse(BaseModel):
    """Response with calibration learning statistics."""
    total_adjustments: int
    severity_bias: Dict
    probability_bias: Dict
    weight_suggestions: Optional[Dict] = None
    message: str


class BatchScoreStatusResponse(BaseModel):
    """Response for batch scoring status."""
    total_counterfactuals: int
    scored: int
    not_scored: int
    failed: int
    completion_percentage: float
    message: str
