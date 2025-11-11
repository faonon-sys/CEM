"""
Sprint 5 API: Trajectory Projection Endpoints
=============================================

REST API endpoints for Phase 5 strategic outcome trajectory projection.

Endpoints:
- POST /api/trajectories/project - Project trajectory from counterfactual
- GET /api/trajectories/{trajectory_id} - Get trajectory details
- POST /api/trajectories/{trajectory_id}/intervention - Test intervention
- GET /api/trajectories/{trajectory_id}/decision-points - Get decision points
- GET /api/trajectories/{trajectory_id}/inflection-points - Get inflection points
- POST /api/trajectories/compare - Compare multiple trajectories
- GET /api/trajectories/export/{trajectory_id} - Export trajectory report
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
import json

from models.database import get_db
from models.user import User
from models.trajectory import (
    TrajectoryProjection,
    TrajectoryDecisionPoint,
    TrajectoryInflectionPoint,
    InterventionScenario,
    TrajectoryComparison
)
from models.phase3_schema import CounterfactualV2
from models.scenario import Scenario
from utils.auth import get_current_user
from services.trajectory_engine import TrajectoryEngine, Trajectory, StateVariables
from services.decision_detection import DecisionPointDetector, InflectionPointDetector
from services.cascade_simulator import CascadeSimulator
from services.trajectory_uncertainty import UncertaintyEngine
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/trajectories", tags=["trajectories"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class ProjectTrajectoryRequest(BaseModel):
    """Request to project a trajectory from a counterfactual"""
    counterfactual_id: str = Field(..., description="Phase 3 counterfactual UUID")
    time_horizons: List[float] = Field([0.25, 0.5, 1.0, 2.0, 5.0], description="Time horizons in years")
    granularity: str = Field("monthly", description="Time granularity: monthly, quarterly, yearly")
    detect_decision_points: bool = Field(True, description="Auto-detect decision points")
    detect_inflection_points: bool = Field(True, description="Auto-detect inflection points")
    baseline_state: Optional[Dict] = Field(None, description="Custom baseline state variables")


class TrajectoryResponse(BaseModel):
    """Trajectory projection response"""
    trajectory_id: str
    counterfactual_id: str
    scenario_id: str
    time_horizon: float
    granularity: str
    baseline_trajectory: List[Dict]
    alternative_branches: List[Dict]
    decision_points: List[Dict]
    inflection_points: List[Dict]
    metadata: Dict
    created_at: str


class InterventionRequest(BaseModel):
    """Request to test an intervention scenario"""
    decision_point_index: int = Field(..., description="Index of decision point for intervention")
    intervention_type: str = Field(..., description="Type: mitigation, acceleration, deflection, containment")
    intervention_name: str = Field(..., description="Name of intervention")
    intervention_description: str = Field(..., description="Detailed description")
    impact_modifier: float = Field(..., ge=0.0, le=2.0, description="Impact modifier (0-2)")
    estimated_cost: Optional[str] = Field("medium", description="Cost: low, medium, high, very_high")
    implementation_timeframe: Optional[str] = Field("short-term", description="Timeframe")


class InterventionResponse(BaseModel):
    """Intervention scenario response"""
    intervention_id: str
    trajectory_id: str
    decision_point_index: int
    intervention_type: str
    projected_trajectory: List[Dict]
    expected_value: float
    roi_estimate: Optional[float]
    time_to_impact_months: float


class CompareRequest(BaseModel):
    """Request to compare trajectories"""
    baseline_trajectory_id: str
    comparison_trajectory_ids: List[str] = Field(..., min_items=1, max_items=5)
    name: Optional[str] = Field("Trajectory Comparison", description="Comparison name")
    description: Optional[str] = Field(None, description="Comparison description")


class ComparisonResponse(BaseModel):
    """Trajectory comparison response"""
    comparison_id: str
    baseline_trajectory: Dict
    comparison_trajectories: List[Dict]
    divergence_points: List[Dict]
    similarity_scores: Dict[str, float]
    created_at: str


# ============================================================================
# Helper Functions
# ============================================================================

def _serialize_trajectory(trajectory: Trajectory) -> Dict:
    """Serialize trajectory engine output to dictionary"""
    from services.trajectory_engine import TrajectoryEngine
    engine = TrajectoryEngine()
    return engine.export_trajectory_json(trajectory)


def _serialize_decision_point(dp) -> Dict:
    """Serialize decision point to dictionary"""
    return {
        'index': dp.index,
        'timestamp': dp.timestamp,
        'criticality_score': dp.criticality_score,
        'alternative_pathways': dp.alternative_pathways,
        'intervention_window': dp.intervention_window,
        'description': dp.description,
        'recommended_action': dp.recommended_action,
        'metadata': dp.metadata
    }


def _serialize_inflection_point(ip) -> Dict:
    """Serialize inflection point to dictionary"""
    return {
        'index': ip.index,
        'timestamp': ip.timestamp,
        'type': ip.type,
        'magnitude': ip.magnitude,
        'triggering_condition': ip.triggering_condition,
        'pre_inflection_trend': ip.pre_inflection_trend,
        'post_inflection_trend': ip.post_inflection_trend,
        'state_change': ip.state_change,
        'metadata': ip.metadata
    }


def _load_dependency_graph(counterfactual: CounterfactualV2) -> Dict:
    """Load dependency graph from counterfactual"""
    # In production, this would fetch from Phase 2 data
    # For now, return a simplified structure
    return {
        'nodes': [
            {'id': 'node_1', 'description': 'Economic impact', 'domain': 'economic', 'magnitude': 0.8},
            {'id': 'node_2', 'description': 'Political consequences', 'domain': 'political', 'magnitude': 0.6},
            {'id': 'node_3', 'description': 'Social effects', 'domain': 'social', 'magnitude': 0.7},
        ],
        'edges': [
            {'source': 'node_1', 'target': 'node_2', 'weight': 0.8, 'delay': 1.0, 'domain': 'political'},
            {'source': 'node_2', 'target': 'node_3', 'weight': 0.7, 'delay': 2.0, 'domain': 'social'},
        ]
    }


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/project", response_model=TrajectoryResponse)
async def project_trajectory(
    request: ProjectTrajectoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Project strategic outcome trajectory from Phase 3 counterfactual.

    This endpoint:
    1. Loads Phase 3 counterfactual data
    2. Retrieves dependency graph from Phase 2
    3. Runs cascade simulation
    4. Projects trajectory with confidence bounds
    5. Detects decision and inflection points (optional)
    6. Stores results in database

    Args:
        request: Projection request parameters
        current_user: Authenticated user
        db: Database session

    Returns:
        Complete trajectory projection with decision/inflection points
    """
    try:
        # Fetch counterfactual
        counterfactual = db.query(CounterfactualV2).filter(
            CounterfactualV2.id == UUID(request.counterfactual_id)
        ).first()

        if not counterfactual:
            raise HTTPException(status_code=404, detail="Counterfactual not found")

        # Check authorization (user must own the scenario)
        scenario = db.query(Scenario).filter(
            Scenario.id == counterfactual.scenario_id
        ).first()

        if not scenario or scenario.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Load dependency graph
        dependency_graph = _load_dependency_graph(counterfactual)

        # Extract breach condition
        breach_condition = {
            'trigger_node': 'node_1',  # Would come from counterfactual data
            'description': counterfactual.narrative[:200] if counterfactual.narrative else 'Breach condition'
        }

        # Initialize trajectory engine
        engine = TrajectoryEngine()

        # Project trajectory
        trajectory = engine.project_trajectory(
            counterfactual_id=request.counterfactual_id,
            scenario_id=str(counterfactual.scenario_id),
            breach_condition=breach_condition,
            dependency_graph=dependency_graph,
            baseline_state=request.baseline_state,
            time_horizons=request.time_horizons,
            granularity=request.granularity
        )

        # Detect decision points if requested
        decision_points_data = []
        if request.detect_decision_points:
            dp_detector = DecisionPointDetector()
            decision_points = dp_detector.detect_bifurcations(trajectory)
            decision_points_data = [_serialize_decision_point(dp) for dp in decision_points]
            trajectory.decision_points = decision_points_data

        # Detect inflection points if requested
        inflection_points_data = []
        if request.detect_inflection_points:
            ip_detector = InflectionPointDetector()
            inflection_points = ip_detector.detect_inflection_points(trajectory)
            inflection_points_data = [_serialize_inflection_point(ip) for ip in inflection_points]
            trajectory.inflection_points = inflection_points_data

        # Serialize trajectory for storage
        trajectory_json = _serialize_trajectory(trajectory)

        # Store in database
        db_trajectory = TrajectoryProjection(
            id=UUID(trajectory.id),
            counterfactual_id=UUID(request.counterfactual_id),
            scenario_id=counterfactual.scenario_id,
            time_horizon=trajectory.time_horizon,
            granularity=trajectory.granularity,
            baseline_trajectory=trajectory_json['baseline_trajectory'],
            alternative_branches=trajectory_json['alternative_branches'],
            cascade_depth=trajectory.metadata.get('cascade_depth'),
            cascade_waves_count=trajectory.metadata.get('cascade_waves_count'),
            affected_domains=trajectory.metadata.get('affected_domains'),
            feedback_loops_count=trajectory.metadata.get('feedback_loops'),
            confidence_level=0.95,
            monte_carlo_simulations=10000,
            computation_metadata=trajectory.metadata
        )
        db.add(db_trajectory)

        # Store decision points
        for dp_data in decision_points_data:
            db_dp = TrajectoryDecisionPoint(
                trajectory_id=UUID(trajectory.id),
                trajectory_index=dp_data['index'],
                timestamp=dp_data['timestamp'],
                criticality_score=dp_data['criticality_score'],
                alternative_pathways=dp_data['alternative_pathways'],
                pathways_count=len(dp_data['alternative_pathways']),
                intervention_window_months=dp_data['intervention_window'],
                description=dp_data['description'],
                recommended_action=dp_data['recommended_action'],
                detection_metadata=dp_data['metadata']
            )
            db.add(db_dp)

        # Store inflection points
        for ip_data in inflection_points_data:
            db_ip = TrajectoryInflectionPoint(
                trajectory_id=UUID(trajectory.id),
                trajectory_index=ip_data['index'],
                timestamp=ip_data['timestamp'],
                inflection_type=ip_data['type'],
                magnitude=ip_data['magnitude'],
                pre_inflection_trend=ip_data['pre_inflection_trend'],
                post_inflection_trend=ip_data['post_inflection_trend'],
                triggering_condition=ip_data['triggering_condition'],
                state_changes=ip_data['state_change'],
                detection_metadata=ip_data['metadata']
            )
            db.add(db_ip)

        db.commit()

        # Return response
        return TrajectoryResponse(
            trajectory_id=trajectory.id,
            counterfactual_id=request.counterfactual_id,
            scenario_id=str(counterfactual.scenario_id),
            time_horizon=trajectory.time_horizon,
            granularity=trajectory.granularity,
            baseline_trajectory=trajectory_json['baseline_trajectory'],
            alternative_branches=trajectory_json['alternative_branches'],
            decision_points=decision_points_data,
            inflection_points=inflection_points_data,
            metadata=trajectory.metadata,
            created_at=trajectory.created_at.isoformat()
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Trajectory projection failed: {str(e)}")


@router.get("/{trajectory_id}", response_model=TrajectoryResponse)
async def get_trajectory(
    trajectory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a trajectory projection by ID.

    Args:
        trajectory_id: Trajectory UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Complete trajectory with decision/inflection points
    """
    try:
        trajectory = db.query(TrajectoryProjection).filter(
            TrajectoryProjection.id == UUID(trajectory_id)
        ).first()

        if not trajectory:
            raise HTTPException(status_code=404, detail="Trajectory not found")

        # Check authorization
        scenario = db.query(Scenario).filter(
            Scenario.id == trajectory.scenario_id
        ).first()

        if not scenario or scenario.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Load decision points
        decision_points = db.query(TrajectoryDecisionPoint).filter(
            TrajectoryDecisionPoint.trajectory_id == UUID(trajectory_id)
        ).all()

        decision_points_data = [{
            'index': dp.trajectory_index,
            'timestamp': float(dp.timestamp),
            'criticality_score': float(dp.criticality_score),
            'alternative_pathways': dp.alternative_pathways,
            'intervention_window': float(dp.intervention_window_months) if dp.intervention_window_months else 6.0,
            'description': dp.description,
            'recommended_action': dp.recommended_action,
            'metadata': dp.detection_metadata
        } for dp in decision_points]

        # Load inflection points
        inflection_points = db.query(TrajectoryInflectionPoint).filter(
            TrajectoryInflectionPoint.trajectory_id == UUID(trajectory_id)
        ).all()

        inflection_points_data = [{
            'index': ip.trajectory_index,
            'timestamp': float(ip.timestamp),
            'type': ip.inflection_type,
            'magnitude': float(ip.magnitude),
            'triggering_condition': ip.triggering_condition,
            'pre_inflection_trend': float(ip.pre_inflection_trend) if ip.pre_inflection_trend else 0.0,
            'post_inflection_trend': float(ip.post_inflection_trend) if ip.post_inflection_trend else 0.0,
            'state_change': ip.state_changes,
            'metadata': ip.detection_metadata
        } for ip in inflection_points]

        return TrajectoryResponse(
            trajectory_id=str(trajectory.id),
            counterfactual_id=str(trajectory.counterfactual_id),
            scenario_id=str(trajectory.scenario_id),
            time_horizon=float(trajectory.time_horizon),
            granularity=trajectory.granularity,
            baseline_trajectory=trajectory.baseline_trajectory,
            alternative_branches=trajectory.alternative_branches or [],
            decision_points=decision_points_data,
            inflection_points=inflection_points_data,
            metadata=trajectory.computation_metadata or {},
            created_at=trajectory.created_at.isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trajectory: {str(e)}")


@router.post("/{trajectory_id}/intervention", response_model=InterventionResponse)
async def test_intervention(
    trajectory_id: str,
    request: InterventionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test an intervention scenario at a decision point.

    Re-projects trajectory with intervention effects applied.

    Args:
        trajectory_id: Trajectory UUID
        request: Intervention parameters
        current_user: Authenticated user
        db: Database session

    Returns:
        Intervention scenario with modified trajectory
    """
    try:
        # Load trajectory
        trajectory_db = db.query(TrajectoryProjection).filter(
            TrajectoryProjection.id == UUID(trajectory_id)
        ).first()

        if not trajectory_db:
            raise HTTPException(status_code=404, detail="Trajectory not found")

        # Check authorization
        scenario = db.query(Scenario).filter(
            Scenario.id == trajectory_db.scenario_id
        ).first()

        if not scenario or scenario.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Load decision point
        decision_point = db.query(TrajectoryDecisionPoint).filter(
            TrajectoryDecisionPoint.trajectory_id == UUID(trajectory_id),
            TrajectoryDecisionPoint.trajectory_index == request.decision_point_index
        ).first()

        # Reconstruct trajectory object
        from services.trajectory_engine import Trajectory, TrajectoryPoint, StateVariables

        baseline_points = []
        for point_data in trajectory_db.baseline_trajectory:
            state = StateVariables(**point_data['state_variables'])
            point = TrajectoryPoint(
                timestamp=point_data['timestamp'],
                state_variables=state,
                confidence_bounds=tuple(point_data['confidence_bounds']),
                cascade_wave=point_data['cascade_wave'],
                metadata=point_data.get('metadata', {})
            )
            baseline_points.append(point)

        trajectory = Trajectory(
            id=str(trajectory_db.id),
            counterfactual_id=str(trajectory_db.counterfactual_id),
            scenario_id=str(trajectory_db.scenario_id),
            time_horizon=float(trajectory_db.time_horizon),
            granularity=trajectory_db.granularity,
            baseline_trajectory=baseline_points,
            alternative_branches=[],
            decision_points=[],
            inflection_points=[],
            metadata=trajectory_db.computation_metadata or {},
            created_at=trajectory_db.created_at
        )

        # Generate intervention branch
        engine = TrajectoryEngine()
        alternative_actions = [{
            'description': request.intervention_description,
            'effects': {'impact_modifier': request.impact_modifier},
            'probability': 0.7
        }]

        branches = engine.generate_branching_trajectories(
            base_trajectory=trajectory,
            decision_point_index=request.decision_point_index,
            alternative_actions=alternative_actions
        )

        if not branches:
            raise HTTPException(status_code=500, detail="Failed to generate intervention branch")

        branch = branches[0]

        # Calculate expected value and ROI
        final_value = branch.trajectory_points[-1].state_variables.primary_metric
        baseline_final = trajectory.baseline_trajectory[-1].state_variables.primary_metric
        expected_value = final_value
        roi_estimate = ((final_value - baseline_final) / baseline_final * 100) if baseline_final > 0 else 0.0

        # Time to impact
        time_to_impact = decision_point.intervention_window_months if decision_point else 6.0

        # Serialize branch trajectory
        projected_trajectory = [{
            'timestamp': p.timestamp,
            'state_variables': {
                'primary_metric': p.state_variables.primary_metric,
                'gdp_impact': p.state_variables.gdp_impact,
                'stability_index': p.state_variables.stability_index,
                'resource_levels': p.state_variables.resource_levels,
                'operational_capability': p.state_variables.operational_capability,
                'social_cohesion': p.state_variables.social_cohesion
            },
            'confidence_bounds': p.confidence_bounds,
            'metadata': p.metadata
        } for p in branch.trajectory_points]

        # Store intervention scenario
        intervention_id = str(UUID(int=hash(trajectory_id + str(request.decision_point_index)) % (2**128)))

        db_intervention = InterventionScenario(
            id=UUID(intervention_id),
            trajectory_id=UUID(trajectory_id),
            decision_point_id=UUID(decision_point.id) if decision_point else None,
            intervention_name=request.intervention_name,
            intervention_description=request.intervention_description,
            intervention_type=request.intervention_type,
            decision_point_index=request.decision_point_index,
            impact_modifier=request.impact_modifier,
            estimated_cost=request.estimated_cost,
            implementation_timeframe=request.implementation_timeframe,
            projected_trajectory=projected_trajectory,
            expected_value=expected_value,
            roi_estimate=roi_estimate,
            time_to_impact_months=time_to_impact,
            creation_metadata={'user_id': str(current_user.id), 'created_at': datetime.utcnow().isoformat()}
        )
        db.add(db_intervention)
        db.commit()

        return InterventionResponse(
            intervention_id=intervention_id,
            trajectory_id=trajectory_id,
            decision_point_index=request.decision_point_index,
            intervention_type=request.intervention_type,
            projected_trajectory=projected_trajectory,
            expected_value=expected_value,
            roi_estimate=roi_estimate,
            time_to_impact_months=time_to_impact
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Intervention test failed: {str(e)}")


@router.get("/{trajectory_id}/decision-points")
async def get_decision_points(
    trajectory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all decision points for a trajectory"""
    trajectory = db.query(TrajectoryProjection).filter(
        TrajectoryProjection.id == UUID(trajectory_id)
    ).first()

    if not trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")

    decision_points = db.query(TrajectoryDecisionPoint).filter(
        TrajectoryDecisionPoint.trajectory_id == UUID(trajectory_id)
    ).order_by(TrajectoryDecisionPoint.timestamp).all()

    return {
        'trajectory_id': trajectory_id,
        'decision_points': [{
            'id': str(dp.id),
            'index': dp.trajectory_index,
            'timestamp': float(dp.timestamp),
            'criticality_score': float(dp.criticality_score),
            'alternative_pathways': dp.alternative_pathways,
            'intervention_window_months': float(dp.intervention_window_months) if dp.intervention_window_months else 6.0,
            'description': dp.description,
            'recommended_action': dp.recommended_action
        } for dp in decision_points]
    }


@router.get("/{trajectory_id}/inflection-points")
async def get_inflection_points(
    trajectory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all inflection points for a trajectory"""
    trajectory = db.query(TrajectoryProjection).filter(
        TrajectoryProjection.id == UUID(trajectory_id)
    ).first()

    if not trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")

    inflection_points = db.query(TrajectoryInflectionPoint).filter(
        TrajectoryInflectionPoint.trajectory_id == UUID(trajectory_id)
    ).order_by(TrajectoryInflectionPoint.timestamp).all()

    return {
        'trajectory_id': trajectory_id,
        'inflection_points': [{
            'id': str(ip.id),
            'index': ip.trajectory_index,
            'timestamp': float(ip.timestamp),
            'type': ip.inflection_type,
            'magnitude': float(ip.magnitude),
            'triggering_condition': ip.triggering_condition,
            'pre_inflection_trend': float(ip.pre_inflection_trend) if ip.pre_inflection_trend else 0.0,
            'post_inflection_trend': float(ip.post_inflection_trend) if ip.post_inflection_trend else 0.0
        } for ip in inflection_points]
    }


# Summary endpoint
@router.get("/scenarios/{scenario_id}/list")
async def list_scenario_trajectories(
    scenario_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all trajectories for a scenario"""
    scenario = db.query(Scenario).filter(
        Scenario.id == UUID(scenario_id)
    ).first()

    if not scenario or scenario.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    trajectories = db.query(TrajectoryProjection).filter(
        TrajectoryProjection.scenario_id == UUID(scenario_id)
    ).order_by(TrajectoryProjection.created_at.desc()).all()

    return {
        'scenario_id': scenario_id,
        'trajectories': [{
            'id': str(t.id),
            'counterfactual_id': str(t.counterfactual_id),
            'time_horizon': float(t.time_horizon),
            'granularity': t.granularity,
            'cascade_depth': t.cascade_depth,
            'created_at': t.created_at.isoformat()
        } for t in trajectories]
    }


# Export endpoint
@router.get("/export/{trajectory_id}")
async def export_trajectory_report(
    trajectory_id: str,
    format: str = Query('json', description="Export format: json, html"),
    template: str = Query('executive', description="Report template: executive, technical, risk_management"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export trajectory report in specified format.

    Supports:
    - JSON: Machine-readable trajectory data
    - HTML: Interactive web dashboard
    - PDF: Executive summary (requires reportlab - not yet implemented)
    - PPTX: Presentation slides (requires python-pptx - not yet implemented)

    Args:
        trajectory_id: Trajectory UUID
        format: Export format ('json', 'html', 'pdf', 'pptx')
        template: Report template type
        current_user: Authenticated user
        db: Database session

    Returns:
        Generated report content with appropriate content type
    """
    from services.report_generator import ReportGenerator
    from fastapi.responses import Response

    try:
        # Load trajectory
        trajectory = db.query(TrajectoryProjection).filter(
            TrajectoryProjection.id == UUID(trajectory_id)
        ).first()

        if not trajectory:
            raise HTTPException(status_code=404, detail="Trajectory not found")

        # Check authorization
        scenario = db.query(Scenario).filter(
            Scenario.id == trajectory.scenario_id
        ).first()

        if not scenario or scenario.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Load decision and inflection points
        decision_points = db.query(TrajectoryDecisionPoint).filter(
            TrajectoryDecisionPoint.trajectory_id == UUID(trajectory_id)
        ).order_by(TrajectoryDecisionPoint.timestamp).all()

        inflection_points = db.query(TrajectoryInflectionPoint).filter(
            TrajectoryInflectionPoint.trajectory_id == UUID(trajectory_id)
        ).order_by(TrajectoryInflectionPoint.timestamp).all()

        # Prepare data
        trajectory_data = {
            'trajectory_id': str(trajectory.id),
            'counterfactual_id': str(trajectory.counterfactual_id),
            'scenario_id': str(trajectory.scenario_id),
            'time_horizon': float(trajectory.time_horizon),
            'granularity': trajectory.granularity,
            'baseline_trajectory': trajectory.baseline_trajectory,
            'alternative_branches': trajectory.alternative_branches or [],
            'metadata': trajectory.computation_metadata or {}
        }

        decision_points_data = [{
            'index': dp.trajectory_index,
            'timestamp': float(dp.timestamp),
            'criticality_score': float(dp.criticality_score),
            'description': dp.description,
            'intervention_window': float(dp.intervention_window_months) if dp.intervention_window_months else 6.0,
            'recommended_action': dp.recommended_action
        } for dp in decision_points]

        inflection_points_data = [{
            'index': ip.trajectory_index,
            'timestamp': float(ip.timestamp),
            'type': ip.inflection_type,
            'magnitude': float(ip.magnitude),
            'triggering_condition': ip.triggering_condition,
            'pre_inflection_trend': float(ip.pre_inflection_trend) if ip.pre_inflection_trend else 0.0,
            'post_inflection_trend': float(ip.post_inflection_trend) if ip.post_inflection_trend else 0.0
        } for ip in inflection_points]

        # Generate report
        generator = ReportGenerator()
        report = generator.generate_report(
            trajectory_data=trajectory_data,
            decision_points=decision_points_data,
            inflection_points=inflection_points_data,
            format=format,
            template=template
        )

        # Return report with appropriate headers
        return Response(
            content=report['content'],
            media_type=report['content_type'],
            headers={
                'Content-Disposition': f'attachment; filename="{report["filename"]}"'
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
