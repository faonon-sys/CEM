"""
Trajectory Projection Pipeline - Celery Tasks
==============================================

Automated pipeline for Phase 3 → Phase 5 trajectory projection.
"""
import logging
from typing import Dict, Optional
from uuid import UUID
import traceback

from celery import Task
from celery_app import app
from sqlalchemy.orm import Session

# Import database models
from models.database import SessionLocal
from models.scenario import Scenario, CounterfactualV2, DependencyGraph
from models.trajectory import TrajectoryProjection, TrajectoryDecisionPoint, TrajectoryInflectionPoint

# Import services
from services.trajectory_engine import TrajectoryEngine
from services.decision_detection import DecisionPointDetector, InflectionPointDetector
from services.cascade_simulator import CascadeSimulator
from services.trajectory_uncertainty import UncertaintyEngine

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
def project_trajectory_pipeline(
    self,
    counterfactual_id: str,
    user_id: str,
    time_horizons: Optional[list] = None,
    granularity: str = 'monthly',
    detect_decision_points: bool = True,
    detect_inflection_points: bool = True
) -> Dict:
    """
    Complete Phase 3 → Phase 5 projection pipeline.

    Pipeline Steps:
    1. Validate Phase 3 counterfactual data
    2. Fetch Phase 2 dependency graph
    3. Run trajectory projection
    4. Detect decision/inflection points
    5. Store results in database
    6. Return trajectory ID

    Args:
        counterfactual_id: UUID of Phase 3 counterfactual
        user_id: User ID for authorization
        time_horizons: List of projection endpoints (default: [0.25, 0.5, 1.0, 2.0, 5.0])
        granularity: 'monthly', 'quarterly', or 'yearly'
        detect_decision_points: Whether to detect decision points
        detect_inflection_points: Whether to detect inflection points

    Returns:
        Dictionary with trajectory_id and status
    """
    try:
        # Step 1: Validate counterfactual
        self.update_state(
            state='VALIDATING',
            meta={'step': 1, 'total': 6, 'message': 'Validating counterfactual data...'}
        )

        db = self.db
        counterfactual = db.query(CounterfactualV2).filter(
            CounterfactualV2.id == UUID(counterfactual_id)
        ).first()

        if not counterfactual:
            raise ValueError(f"Counterfactual {counterfactual_id} not found")

        # Verify ownership
        scenario = db.query(Scenario).filter(
            Scenario.id == counterfactual.scenario_id
        ).first()

        if not scenario or str(scenario.user_id) != user_id:
            raise PermissionError(f"User {user_id} does not have access to this counterfactual")

        # Validate breach condition
        if not counterfactual.breach_condition:
            raise ValueError("Counterfactual missing breach condition")

        logger.info(f"✓ Counterfactual {counterfactual_id} validated")

        # Step 2: Fetch dependency graph
        self.update_state(
            state='LOADING_DEPENDENCIES',
            meta={'step': 2, 'total': 6, 'message': 'Loading dependency graph...'}
        )

        dependency_graph_obj = db.query(DependencyGraph).filter(
            DependencyGraph.scenario_id == counterfactual.scenario_id
        ).first()

        if not dependency_graph_obj:
            # Create minimal dependency graph if not exists
            logger.warning(f"No dependency graph found for scenario {counterfactual.scenario_id}, using minimal graph")
            dependency_graph = {
                'nodes': [],
                'edges': []
            }
        else:
            dependency_graph = {
                'nodes': dependency_graph_obj.nodes or [],
                'edges': dependency_graph_obj.edges or []
            }

        logger.info(f"✓ Loaded dependency graph with {len(dependency_graph['nodes'])} nodes")

        # Step 3: Project trajectory
        self.update_state(
            state='PROJECTING',
            meta={'step': 3, 'total': 6, 'message': 'Projecting trajectory...'}
        )

        if time_horizons is None:
            time_horizons = [0.25, 0.5, 1.0, 2.0, 5.0]

        # Initialize engines
        uncertainty_engine = UncertaintyEngine()
        cascade_simulator = CascadeSimulator()
        trajectory_engine = TrajectoryEngine(
            uncertainty_engine=uncertainty_engine,
            cascade_simulator=cascade_simulator
        )

        # Project trajectory
        trajectory = trajectory_engine.project_trajectory(
            counterfactual_id=str(counterfactual.id),
            scenario_id=str(counterfactual.scenario_id),
            breach_condition=counterfactual.breach_condition,
            dependency_graph=dependency_graph,
            time_horizons=time_horizons,
            granularity=granularity
        )

        logger.info(f"✓ Trajectory projected with {len(trajectory.baseline_trajectory)} points")

        # Step 4: Detect decision and inflection points
        decision_points_data = []
        inflection_points_data = []

        if detect_decision_points:
            self.update_state(
                state='ANALYZING_DECISIONS',
                meta={'step': 4, 'total': 6, 'message': 'Detecting decision points...'}
            )

            decision_detector = DecisionPointDetector()
            decision_points = decision_detector.detect_bifurcations(trajectory)

            for dp in decision_points:
                decision_points_data.append({
                    'trajectory_index': dp.trajectory_index,
                    'timestamp': float(dp.timestamp),
                    'criticality_score': float(dp.criticality_score),
                    'impact_score': float(dp.impact_score),
                    'reversibility_score': float(dp.reversibility_score),
                    'time_sensitivity_score': float(dp.time_sensitivity_score),
                    'alternative_pathways': dp.alternative_pathways,
                    'pathways_count': len(dp.alternative_pathways),
                    'intervention_window_months': float(dp.intervention_window_months),
                    'description': dp.description,
                    'recommended_action': dp.recommended_action,
                    'detection_metadata': dp.detection_metadata
                })

            logger.info(f"✓ Detected {len(decision_points)} decision points")

        if detect_inflection_points:
            self.update_state(
                state='ANALYZING_INFLECTIONS',
                meta={'step': 4, 'total': 6, 'message': 'Detecting inflection points...'}
            )

            inflection_detector = InflectionPointDetector()
            inflection_points = inflection_detector.detect_all_inflection_points(trajectory)

            for ip in inflection_points:
                inflection_points_data.append({
                    'trajectory_index': ip.trajectory_index,
                    'timestamp': float(ip.timestamp),
                    'inflection_type': ip.inflection_type,
                    'magnitude': float(ip.magnitude),
                    'pre_inflection_trend': float(ip.pre_inflection_trend) if ip.pre_inflection_trend else None,
                    'post_inflection_trend': float(ip.post_inflection_trend) if ip.post_inflection_trend else None,
                    'triggering_condition': ip.triggering_condition,
                    'state_changes': ip.state_changes,
                    'detection_metadata': ip.detection_metadata
                })

            logger.info(f"✓ Detected {len(inflection_points)} inflection points")

        # Step 5: Store in database
        self.update_state(
            state='STORING',
            meta={'step': 5, 'total': 6, 'message': 'Storing trajectory in database...'}
        )

        # Export trajectory to JSON
        trajectory_json = trajectory_engine.export_trajectory_json(trajectory)

        # Create trajectory projection record
        trajectory_projection = TrajectoryProjection(
            counterfactual_id=UUID(counterfactual_id),
            scenario_id=counterfactual.scenario_id,
            time_horizon=trajectory.time_horizon,
            granularity=trajectory.granularity,
            baseline_trajectory=trajectory_json['baseline_trajectory'],
            alternative_branches=trajectory_json.get('alternative_branches'),
            cascade_depth=trajectory.metadata.get('cascade_depth'),
            cascade_waves_count=trajectory.metadata.get('cascade_waves_count'),
            affected_domains=trajectory.metadata.get('affected_domains'),
            feedback_loops_count=trajectory.metadata.get('feedback_loops', 0),
            confidence_level=0.95,
            monte_carlo_simulations=10000,
            computation_metadata=trajectory.metadata
        )

        db.add(trajectory_projection)
        db.commit()
        db.refresh(trajectory_projection)

        trajectory_id = str(trajectory_projection.id)
        logger.info(f"✓ Stored trajectory {trajectory_id}")

        # Store decision points
        if decision_points_data:
            for dp_data in decision_points_data:
                decision_point = TrajectoryDecisionPoint(
                    trajectory_id=trajectory_projection.id,
                    **dp_data
                )
                db.add(decision_point)

            db.commit()
            logger.info(f"✓ Stored {len(decision_points_data)} decision points")

        # Store inflection points
        if inflection_points_data:
            for ip_data in inflection_points_data:
                inflection_point = TrajectoryInflectionPoint(
                    trajectory_id=trajectory_projection.id,
                    **ip_data
                )
                db.add(inflection_point)

            db.commit()
            logger.info(f"✓ Stored {len(inflection_points_data)} inflection points")

        # Step 6: Complete
        self.update_state(
            state='SUCCESS',
            meta={'step': 6, 'total': 6, 'message': 'Pipeline completed successfully'}
        )

        return {
            'status': 'completed',
            'trajectory_id': trajectory_id,
            'counterfactual_id': counterfactual_id,
            'decision_points_count': len(decision_points_data),
            'inflection_points_count': len(inflection_points_data),
            'trajectory_points_count': len(trajectory.baseline_trajectory),
            'cascade_depth': trajectory.metadata.get('cascade_depth'),
            'cascade_waves_count': trajectory.metadata.get('cascade_waves_count')
        }

    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        return {
            'status': 'failed',
            'error': 'permission_denied',
            'message': str(e)
        }

    except ValueError as e:
        # Don't retry validation errors
        logger.error(f"Validation error: {e}")
        return {
            'status': 'failed',
            'error': 'validation_error',
            'message': str(e)
        }

    except Exception as exc:
        # Log full traceback
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
def check_pipeline_status(task_id: str) -> Dict:
    """
    Check status of trajectory projection pipeline.

    Args:
        task_id: Celery task ID

    Returns:
        Dictionary with task status and result
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=app)

    return {
        'task_id': task_id,
        'state': result.state,
        'info': result.info if result.info else {},
        'ready': result.ready(),
        'successful': result.successful() if result.ready() else False,
        'failed': result.failed() if result.ready() else False
    }
