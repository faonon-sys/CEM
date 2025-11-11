"""
API endpoints for counterfactual scoring system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time
import logging
from uuid import UUID

from models.database import get_db
from models.scenario import Counterfactual
from models.scoring import CounterfactualScore, ScoringAdjustment
from models.user import User
from schemas.scoring import (
    ComputeScoresRequest,
    ComputeScoresResponse,
    CounterfactualScoreResponse,
    CalibrateScoreRequest,
    CalibrateScoreResponse,
    SensitivityAnalysisResponse,
    MonteCarloSimulationRequest,
    MonteCarloSimulationResponse,
    CalibrationStatisticsResponse,
    BatchScoreStatusResponse
)
from services.scoring_engine import (
    ScoringEngine,
    CalibrationEngine,
    extract_severity_factors_from_counterfactual,
    extract_probability_factors_from_counterfactual
)
from utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Global calibration engine instance (in production, use Redis or DB storage)
calibration_engine = CalibrationEngine()


@router.post("/api/scoring/compute", response_model=ComputeScoresResponse)
async def compute_scores(
    request: ComputeScoresRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compute severity and probability scores for counterfactuals.

    Calculates multi-factor scores with confidence intervals.
    """
    start_time = time.time()

    # Initialize scoring engine with custom weights if provided
    engine_kwargs = {}
    if request.weights and request.weights.severity_weights:
        engine_kwargs['severity_weights'] = request.weights.severity_weights
    if request.weights and request.weights.probability_weights:
        engine_kwargs['probability_weights'] = request.weights.probability_weights

    scoring_engine = ScoringEngine(**engine_kwargs)

    scores_computed = []

    for cf_id in request.counterfactual_ids:
        try:
            # Fetch counterfactual
            counterfactual = db.query(Counterfactual).filter(
                Counterfactual.id == cf_id
            ).first()

            if not counterfactual:
                logger.warning(f"Counterfactual {cf_id} not found, skipping")
                continue

            # Check if score already exists
            existing_score = db.query(CounterfactualScore).filter(
                CounterfactualScore.counterfactual_id == cf_id
            ).first()

            if existing_score and not request.force_recompute:
                logger.info(f"Score already exists for {cf_id}, using existing")
                scores_computed.append(existing_score.to_dict())
                continue

            # Prepare counterfactual data for extraction
            cf_data = {
                'consequences': counterfactual.consequences,
                'estimated_severity': float(counterfactual.severity_rating) / 10.0 if counterfactual.severity_rating else 0.5,
                'breach_conditions': [counterfactual.breach_condition],
                'description': counterfactual.breach_condition,
                'fragility_evidence_score': 0.6,  # Default, can be enhanced
                'historical_precedent': False,
                'precedent_count': 0,
                'time_horizon': 'medium'
            }

            # Extract factors
            severity_factors = extract_severity_factors_from_counterfactual(cf_data)
            probability_factors = extract_probability_factors_from_counterfactual(cf_data)

            # Calculate scores
            severity_result = scoring_engine.calculate_severity(severity_factors)
            probability_result = scoring_engine.calculate_probability(probability_factors)

            # Calculate risk score
            risk_score = severity_result.score * probability_result.score

            # Store or update score in database
            if existing_score:
                score_record = existing_score
            else:
                score_record = CounterfactualScore(counterfactual_id=cf_id)
                db.add(score_record)

            # Update score record
            score_record.severity_score = severity_result.score
            score_record.severity_ci_lower = severity_result.confidence_interval[0]
            score_record.severity_ci_upper = severity_result.confidence_interval[1]
            score_record.severity_cascade_depth = severity_factors.cascade_depth
            score_record.severity_breadth_of_impact = severity_factors.breadth_of_impact
            score_record.severity_deviation_magnitude = severity_factors.deviation_magnitude
            score_record.severity_irreversibility = severity_factors.irreversibility
            score_record.severity_sensitivity = severity_result.sensitivity

            score_record.probability_score = probability_result.score
            score_record.probability_ci_lower = probability_result.confidence_interval[0]
            score_record.probability_ci_upper = probability_result.confidence_interval[1]
            score_record.probability_fragility_strength = probability_factors.fragility_strength
            score_record.probability_historical_precedent = probability_factors.historical_precedent
            score_record.probability_dependency_failures = probability_factors.dependency_failures
            score_record.probability_time_horizon = probability_factors.time_horizon
            score_record.probability_sensitivity = probability_result.sensitivity

            score_record.risk_score = risk_score
            score_record.severity_weights = scoring_engine.severity_weights
            score_record.probability_weights = scoring_engine.probability_weights

            db.commit()
            db.refresh(score_record)

            scores_computed.append(score_record.to_dict())

            logger.info(f"Computed score for {cf_id}: severity={severity_result.score:.3f}, probability={probability_result.score:.3f}")

        except Exception as e:
            logger.error(f"Error computing score for {cf_id}: {str(e)}", exc_info=True)
            continue

    computation_time = time.time() - start_time

    return ComputeScoresResponse(
        scores=scores_computed,
        computation_time=computation_time,
        message=f"Computed scores for {len(scores_computed)} counterfactuals in {computation_time:.2f}s"
    )


@router.get("/api/scoring/{counterfactual_id}", response_model=CounterfactualScoreResponse)
async def get_score(
    counterfactual_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve existing score for a counterfactual.
    """
    score = db.query(CounterfactualScore).filter(
        CounterfactualScore.counterfactual_id == counterfactual_id
    ).first()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score not found for counterfactual {counterfactual_id}"
        )

    return score.to_dict()


@router.put("/api/scoring/calibrate/{counterfactual_id}", response_model=CalibrateScoreResponse)
async def calibrate_score(
    counterfactual_id: UUID,
    request: CalibrateScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calibrate (adjust) a score based on expert judgment.
    """
    # Fetch existing score
    score = db.query(CounterfactualScore).filter(
        CounterfactualScore.counterfactual_id == counterfactual_id
    ).first()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score not found for counterfactual {counterfactual_id}"
        )

    # Record original values
    original_severity = float(score.severity_score)
    original_probability = float(score.probability_score)

    # Update calibrated values
    score.is_calibrated = True
    score.calibrated_severity = request.severity_adjustment
    score.calibrated_probability = request.probability_adjustment
    score.calibrated_by_user_id = current_user.id
    score.calibration_timestamp = time.time()
    score.calibration_rationale = request.rationale

    # Calculate deltas
    severity_delta = request.severity_adjustment - original_severity
    probability_delta = request.probability_adjustment - original_probability

    # Record adjustment for learning
    adjustment = ScoringAdjustment(
        score_id=score.id,
        original_severity=original_severity,
        original_probability=original_probability,
        adjusted_severity=request.severity_adjustment,
        adjusted_probability=request.probability_adjustment,
        severity_delta=severity_delta,
        probability_delta=probability_delta,
        adjusted_by_user_id=current_user.id,
        rationale=request.rationale
    )
    db.add(adjustment)

    # Record in calibration engine for learning
    calibration_engine.record_adjustment(
        counterfactual_id=str(counterfactual_id),
        original_severity=original_severity,
        adjusted_severity=request.severity_adjustment,
        original_probability=original_probability,
        adjusted_probability=request.probability_adjustment,
        expert_rationale=request.rationale
    )

    db.commit()
    db.refresh(score)

    return CalibrateScoreResponse(
        score_id=score.id,
        updated_score=score.to_dict(),
        adjustment_delta={
            'severity': severity_delta,
            'probability': probability_delta
        },
        message="Score calibrated successfully"
    )


@router.get("/api/scoring/sensitivity/{counterfactual_id}", response_model=SensitivityAnalysisResponse)
async def get_sensitivity_analysis(
    counterfactual_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sensitivity analysis showing which factors influence scores most.
    """
    score = db.query(CounterfactualScore).filter(
        CounterfactualScore.counterfactual_id == counterfactual_id
    ).first()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score not found for counterfactual {counterfactual_id}"
        )

    # Find most influential factors
    severity_sensitivity = score.severity_sensitivity or {}
    probability_sensitivity = score.probability_sensitivity or {}

    most_influential = {
        'severity': max(severity_sensitivity, key=severity_sensitivity.get) if severity_sensitivity else None,
        'probability': max(probability_sensitivity, key=probability_sensitivity.get) if probability_sensitivity else None
    }

    return SensitivityAnalysisResponse(
        counterfactual_id=counterfactual_id,
        severity_sensitivity=severity_sensitivity,
        probability_sensitivity=probability_sensitivity,
        most_influential_factors=most_influential,
        message="Sensitivity analysis completed"
    )


@router.post("/api/scoring/monte-carlo", response_model=MonteCarloSimulationResponse)
async def run_monte_carlo(
    request: MonteCarloSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run Monte Carlo simulation to estimate risk distribution.
    """
    # Fetch counterfactual and score
    counterfactual = db.query(Counterfactual).filter(
        Counterfactual.id == request.counterfactual_id
    ).first()

    if not counterfactual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Counterfactual {request.counterfactual_id} not found"
        )

    score = db.query(CounterfactualScore).filter(
        CounterfactualScore.counterfactual_id == request.counterfactual_id
    ).first()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score not found for counterfactual {request.counterfactual_id}. Compute score first."
        )

    # Prepare counterfactual data
    cf_data = {
        'consequences': counterfactual.consequences,
        'estimated_severity': float(counterfactual.severity_rating) / 10.0 if counterfactual.severity_rating else 0.5,
        'breach_conditions': [counterfactual.breach_condition],
        'description': counterfactual.breach_condition,
        'fragility_evidence_score': 0.6,
        'historical_precedent': False,
        'precedent_count': 0,
        'time_horizon': 'medium'
    }

    # Extract factors
    severity_factors = extract_severity_factors_from_counterfactual(cf_data)
    probability_factors = extract_probability_factors_from_counterfactual(cf_data)

    # Run Monte Carlo simulation
    scoring_engine = ScoringEngine()
    simulation_results = scoring_engine.monte_carlo_simulation(
        severity_factors,
        probability_factors,
        n_simulations=request.n_simulations
    )

    return MonteCarloSimulationResponse(
        counterfactual_id=request.counterfactual_id,
        severity=simulation_results['severity'],
        probability=simulation_results['probability'],
        risk=simulation_results['risk'],
        message=f"Monte Carlo simulation completed with {request.n_simulations} iterations"
    )


@router.get("/api/scoring/calibration/statistics", response_model=CalibrationStatisticsResponse)
async def get_calibration_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get calibration statistics for learning algorithm.
    """
    stats = calibration_engine.get_adjustment_statistics()

    # Get weight suggestions if enough data
    weight_suggestions = None
    if len(calibration_engine.adjustments) >= 10:
        scoring_engine = ScoringEngine()
        weight_suggestions = calibration_engine.suggest_weight_corrections(scoring_engine)

    return CalibrationStatisticsResponse(
        total_adjustments=stats.get('total_adjustments', 0),
        severity_bias=stats.get('severity_bias', {}),
        probability_bias=stats.get('probability_bias', {}),
        weight_suggestions=weight_suggestions,
        message="Calibration statistics retrieved"
    )


@router.get("/api/scoring/status/batch", response_model=BatchScoreStatusResponse)
async def get_batch_status(
    scenario_id: UUID = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get batch scoring status for a scenario or all scenarios.
    """
    # Query counterfactuals
    query = db.query(Counterfactual)
    if scenario_id:
        query = query.filter(Counterfactual.scenario_id == scenario_id)

    total_counterfactuals = query.count()

    # Count scored counterfactuals
    scored_query = query.join(CounterfactualScore)
    scored = scored_query.count()

    not_scored = total_counterfactuals - scored
    completion_percentage = (scored / total_counterfactuals * 100) if total_counterfactuals > 0 else 0

    return BatchScoreStatusResponse(
        total_counterfactuals=total_counterfactuals,
        scored=scored,
        not_scored=not_scored,
        failed=0,  # Can be enhanced with failure tracking
        completion_percentage=completion_percentage,
        message=f"Scoring status: {scored}/{total_counterfactuals} completed ({completion_percentage:.1f}%)"
    )
