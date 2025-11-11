"""
Phase 5 Database Schema: Strategic Outcome Trajectory Projections
Sprint 5 - Database Models

This module defines the database schema for storing trajectory projections,
decision points, inflection points, and intervention scenarios.
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from models.database import Base


class TrajectoryProjection(Base):
    """
    Strategic outcome trajectory projection from Phase 3 counterfactuals.

    Stores complete timeline projections with confidence bounds and
    metadata for visualization and analysis.
    """
    __tablename__ = "trajectory_projections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counterfactual_id = Column(UUID(as_uuid=True), ForeignKey("counterfactuals_v2.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)

    # Trajectory configuration
    time_horizon = Column(Numeric(5, 2), nullable=False)  # Years (e.g., 5.00)
    granularity = Column(String(20), nullable=False)  # 'monthly', 'quarterly', 'yearly'

    # Trajectory data
    baseline_trajectory = Column(JSONB, nullable=False)  # Array of TrajectoryPoint objects
    alternative_branches = Column(JSONB)  # Array of TrajectoryBranch objects

    # Cascade metadata
    cascade_depth = Column(Integer)  # Number of cascade waves
    cascade_waves_count = Column(Integer)
    affected_domains = Column(JSONB)  # {domain: count}
    feedback_loops_count = Column(Integer)

    # Confidence metadata
    confidence_level = Column(Numeric(3, 2), default=0.95)  # 95% default
    monte_carlo_simulations = Column(Integer, default=10000)

    # Metadata
    computation_metadata = Column(JSONB)  # Engine settings, timestamps, etc.
    tags = Column(JSONB)  # User-defined tags

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    counterfactual = relationship("CounterfactualV2")
    scenario = relationship("Scenario")
    decision_points = relationship("TrajectoryDecisionPoint", back_populates="trajectory", cascade="all, delete-orphan")
    inflection_points = relationship("TrajectoryInflectionPoint", back_populates="trajectory", cascade="all, delete-orphan")
    interventions = relationship("InterventionScenario", back_populates="trajectory", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TrajectoryProjection(id={self.id}, horizon={self.time_horizon}y, depth={self.cascade_depth})>"


class TrajectoryDecisionPoint(Base):
    """
    Critical decision points in trajectory where strategic choices can
    alter the outcome path.

    Identified automatically by decision point detection algorithms.
    """
    __tablename__ = "trajectory_decision_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trajectory_id = Column(UUID(as_uuid=True), ForeignKey("trajectory_projections.id", ondelete="CASCADE"), nullable=False, index=True)

    # Decision point details
    trajectory_index = Column(Integer, nullable=False)  # Index in baseline trajectory
    timestamp = Column(Numeric(5, 2), nullable=False)  # Years from T=0

    # Criticality metrics
    criticality_score = Column(Numeric(4, 3), nullable=False)  # 0.000-1.000
    impact_score = Column(Numeric(4, 3))
    reversibility_score = Column(Numeric(4, 3))
    time_sensitivity_score = Column(Numeric(4, 3))

    # Alternative pathways
    alternative_pathways = Column(JSONB, nullable=False)  # Array of pathway objects
    pathways_count = Column(Integer)

    # Intervention window
    intervention_window_months = Column(Numeric(5, 1))  # Optimal intervention window

    # Descriptive content
    description = Column(Text, nullable=False)
    recommended_action = Column(Text)

    # Metadata
    detection_metadata = Column(JSONB)  # Detection algorithm details

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trajectory = relationship("TrajectoryProjection", back_populates="decision_points")

    def __repr__(self):
        return f"<TrajectoryDecisionPoint(id={self.id}, T={self.timestamp}y, criticality={self.criticality_score})>"


class TrajectoryInflectionPoint(Base):
    """
    Inflection points (regime changes, threshold crossings) in trajectory.

    Mark significant changes in trajectory trends or state transitions.
    """
    __tablename__ = "trajectory_inflection_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trajectory_id = Column(UUID(as_uuid=True), ForeignKey("trajectory_projections.id", ondelete="CASCADE"), nullable=False, index=True)

    # Inflection point details
    trajectory_index = Column(Integer, nullable=False)
    timestamp = Column(Numeric(5, 2), nullable=False)  # Years from T=0

    # Inflection type and characteristics
    inflection_type = Column(String(50), nullable=False)  # 'acceleration', 'deceleration', 'reversal', 'threshold_crossing'
    magnitude = Column(Numeric(5, 3), nullable=False)  # Magnitude of change

    # Trend analysis
    pre_inflection_trend = Column(Numeric(6, 3))  # Slope before inflection
    post_inflection_trend = Column(Numeric(6, 3))  # Slope after inflection

    # Causal analysis
    triggering_condition = Column(Text, nullable=False)  # What caused this inflection
    state_changes = Column(JSONB)  # Changes in state variables

    # Metadata
    detection_metadata = Column(JSONB)  # Second derivative, thresholds, etc.

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trajectory = relationship("TrajectoryProjection", back_populates="inflection_points")

    def __repr__(self):
        return f"<TrajectoryInflectionPoint(id={self.id}, T={self.timestamp}y, type={self.inflection_type})>"


class InterventionScenario(Base):
    """
    Hypothetical intervention scenarios testing strategic actions at
    decision points.

    Allows 'what-if' analysis of different intervention strategies.
    """
    __tablename__ = "intervention_scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trajectory_id = Column(UUID(as_uuid=True), ForeignKey("trajectory_projections.id", ondelete="CASCADE"), nullable=False, index=True)
    decision_point_id = Column(UUID(as_uuid=True), ForeignKey("trajectory_decision_points.id", ondelete="SET NULL"), index=True)

    # Intervention details
    intervention_name = Column(String(255), nullable=False)
    intervention_description = Column(Text, nullable=False)
    intervention_type = Column(String(50), nullable=False)  # 'mitigation', 'acceleration', 'deflection', 'containment'

    # Intervention parameters
    decision_point_index = Column(Integer, nullable=False)  # Where intervention occurs
    impact_modifier = Column(Numeric(4, 2), nullable=False)  # Effect on cascade (0-2)

    # Cost and feasibility
    estimated_cost = Column(String(50))  # 'low', 'medium', 'high', 'very_high'
    feasibility_score = Column(Numeric(3, 2))  # 0.00-1.00
    implementation_timeframe = Column(String(50))  # 'immediate', 'short-term', 'medium-term', 'long-term'

    # Projected outcomes
    projected_trajectory = Column(JSONB, nullable=False)  # Modified trajectory with intervention
    expected_value = Column(Numeric(5, 3))  # Expected outcome value
    roi_estimate = Column(Numeric(6, 2))  # Return on investment (ratio)
    time_to_impact_months = Column(Numeric(5, 1))  # How long until intervention effects manifest

    # Metadata
    creation_metadata = Column(JSONB)  # User, timestamp, assumptions
    tags = Column(JSONB)  # User-defined tags

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trajectory = relationship("TrajectoryProjection", back_populates="interventions")
    decision_point = relationship("TrajectoryDecisionPoint")

    def __repr__(self):
        return f"<InterventionScenario(id={self.id}, type={self.intervention_type}, ROI={self.roi_estimate})>"


class TrajectoryComparison(Base):
    """
    Saved trajectory comparisons for side-by-side analysis.

    Allows users to save and revisit specific trajectory comparisons.
    """
    __tablename__ = "trajectory_comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)

    # Comparison details
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Trajectories being compared
    baseline_trajectory_id = Column(UUID(as_uuid=True), ForeignKey("trajectory_projections.id", ondelete="CASCADE"), nullable=False)
    comparison_trajectory_ids = Column(JSONB, nullable=False)  # Array of trajectory UUIDs

    # Comparison metrics
    divergence_points = Column(JSONB)  # Where trajectories significantly diverge
    similarity_score = Column(Numeric(3, 2))  # 0-1 similarity between trajectories

    # Metadata
    tags = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    scenario = relationship("Scenario")
    baseline_trajectory = relationship("TrajectoryProjection", foreign_keys=[baseline_trajectory_id])

    def __repr__(self):
        return f"<TrajectoryComparison(id={self.id}, name={self.name})>"


class TrajectoryExport(Base):
    """
    Exported trajectory reports and visualizations.

    Tracks generated exports for caching and audit purposes.
    """
    __tablename__ = "trajectory_exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trajectory_id = Column(UUID(as_uuid=True), ForeignKey("trajectory_projections.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Export details
    export_format = Column(String(20), nullable=False)  # 'pdf', 'json', 'pptx', 'html'
    export_template = Column(String(50))  # 'executive', 'technical', 'risk_management'

    # File details
    file_path = Column(String(500))  # Path to exported file
    file_size_bytes = Column(Integer)

    # Export configuration
    export_config = Column(JSONB)  # Template settings, included data, etc.

    # Generation metadata
    generation_time_ms = Column(Integer)  # How long export took

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    trajectory = relationship("TrajectoryProjection")
    user = relationship("User")

    def __repr__(self):
        return f"<TrajectoryExport(id={self.id}, format={self.export_format})>"
