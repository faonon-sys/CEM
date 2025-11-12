from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.database import Base

"""
Phase 3 Enhanced Schema: Six-Axis Counterfactual Framework
Sprint 4 - Task 1: Data Schema Design

This module extends the existing schema with comprehensive Phase 3 structures:
- Six strategic axes definitions
- Breach conditions with plausibility scoring
- Counterfactuals with divergence timelines
- Consequence chains with cascade depth tracking
- Scenario relationships and lineage
- Fragility linkage from Phase 2
"""
from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from models.database import Base


class CounterfactualAxis(Base):
    """
    Strategic axes for counterfactual generation.
    Defines the six dimensions along which scenarios can diverge.
    """
    __tablename__ = "counterfactual_axes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    prompt_template = Column(Text, nullable=False)
    meta = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    breach_conditions = relationship("BreachCondition", back_populates="axis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CounterfactualAxis(name={self.name})>"


class FragilityPoint(Base):
    """
    Fragility points identified in Phase 2 deep questioning.
    Links fragilities to counterfactual generation.
    """
    __tablename__ = "fragility_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    surface_analysis_id = Column(UUID(as_uuid=True), ForeignKey("surface_analyses.id", ondelete="CASCADE"), index=True)

    # Fragility details
    assumption_id = Column(String(50), nullable=False)  # Reference to assumption
    fragility_score = Column(Numeric(4, 2), nullable=False)  # 0.00-10.00
    breach_probability = Column(Numeric(3, 2), nullable=False)  # 0.00-1.00
    impact_radius = Column(JSONB, nullable=False)  # Array of dependent assumption IDs
    evidence_gaps = Column(JSONB, nullable=False)  # Array of evidence gap strings
    markers = Column(JSONB)  # Linguistic markers (uncertainty, weakness, etc.)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    scenario = relationship("Scenario")
    surface_analysis = relationship("SurfaceAnalysis")
    breach_conditions = relationship("BreachCondition", back_populates="fragility", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FragilityPoint(id={self.id}, score={self.fragility_score}, severity={self.severity})>"


class BreachCondition(Base):
    """
    Specific breach conditions that would invalidate baseline assumptions.
    Generated for each fragility across relevant strategic axes.
    """
    __tablename__ = "breach_conditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    axis_id = Column(UUID(as_uuid=True), ForeignKey("counterfactual_axes.id", ondelete="CASCADE"), nullable=False, index=True)
    fragility_id = Column(UUID(as_uuid=True), ForeignKey("fragility_points.id", ondelete="CASCADE"), nullable=False, index=True)

    # Breach details
    trigger_event = Column(Text, nullable=False)  # Specific, observable event
    description = Column(Text, nullable=False)  # Detailed breach description
    preconditions = Column(JSONB, nullable=False)  # Array of required preconditions
    plausibility_score = Column(Numeric(3, 2), nullable=False)  # 0.00-1.00

    # Metadata
    reasoning = Column(Text)  # LLM reasoning for this breach
    meta = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    axis = relationship("CounterfactualAxis", back_populates="breach_conditions")
    fragility = relationship("FragilityPoint", back_populates="breach_conditions")
    counterfactuals_v2 = relationship("CounterfactualV2", back_populates="breach_condition", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BreachCondition(id={self.id}, plausibility={self.plausibility_score})>"


class CounterfactualV2(Base):
    """
    Enhanced counterfactual scenario with full divergence and consequence tracking.
    Extends the original Counterfactual model with Phase 3 enhancements.
    """
    __tablename__ = "counterfactuals_v2"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    breach_id = Column(UUID(as_uuid=True), ForeignKey("breach_conditions.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)

    # Counterfactual content
    narrative = Column(Text, nullable=False)  # 200-400 word narrative
    divergence_timeline = Column(JSONB, nullable=False)  # Array of divergence points
    affected_domains = Column(JSONB, nullable=False)  # Political, economic, operational, etc.

    # Scoring (calculated by Task 4)
    severity = Column(Numeric(4, 2))  # 0.00-10.00 calculated score
    severity_confidence = Column(JSONB)  # [lower, upper] 90% confidence interval
    probability = Column(Numeric(3, 2))  # 0.00-1.00 calculated score
    probability_confidence = Column(JSONB)  # [lower, upper] 90% confidence interval
    factor_breakdown = Column(JSONB)  # Detailed scoring factor breakdown

    # Metadata
    generation_meta = Column("generation_metadata", JSON, nullable=True, default=dict)
    tags = Column(JSONB)  # User-defined tags for filtering
    selected_for_phase5 = Column(Boolean, default=False)  # Phase 5 selection flag

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    breach_condition = relationship("BreachCondition", back_populates="counterfactuals_v2")
    scenario = relationship("Scenario")
    consequence_chains = relationship("ConsequenceChain", back_populates="counterfactual", cascade="all, delete-orphan")
    relationships_as_parent = relationship("ScenarioRelationship",
                                          foreign_keys="ScenarioRelationship.parent_id",
                                          back_populates="parent_scenario",
                                          cascade="all, delete-orphan")
    relationships_as_child = relationship("ScenarioRelationship",
                                         foreign_keys="ScenarioRelationship.child_id",
                                         back_populates="child_scenario",
                                         cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CounterfactualV2(id={self.id}, severity={self.severity}, probability={self.probability})>"


class ConsequenceChain(Base):
    """
    Cascading consequence chains resulting from breach conditions.
    Tracks multi-level cause-effect relationships.
    """
    __tablename__ = "consequence_chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counterfactual_id = Column(UUID(as_uuid=True), ForeignKey("counterfactuals_v2.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_consequence_id = Column(UUID(as_uuid=True), ForeignKey("consequence_chains.id", ondelete="CASCADE"), index=True)

    # Consequence details
    depth = Column(Integer, nullable=False)  # Level in cascade (1-5)
    description = Column(Text, nullable=False)
    affected_domains = Column(JSONB, nullable=False)  # Domains impacted at this level
    affected_actors = Column(JSONB)  # Actors impacted
    affected_resources = Column(JSONB)  # Resources impacted
    timeframe = Column(String(50))  # When this consequence manifests

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    counterfactual = relationship("CounterfactualV2", back_populates="consequence_chains")
    parent_consequence = relationship("ConsequenceChain", remote_side=[id], backref="child_consequences")

    def __repr__(self):
        return f"<ConsequenceChain(id={self.id}, depth={self.depth})>"


class ScenarioRelationship(Base):
    """
    Relationships between counterfactual scenarios.
    Tracks dependencies, contradictions, and causal links.
    """
    __tablename__ = "scenario_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("counterfactuals_v2.id", ondelete="CASCADE"), nullable=False, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey("counterfactuals_v2.id", ondelete="CASCADE"), nullable=False, index=True)

    relationship_type = Column(String(50), nullable=False)  # dependency, causation, contradiction
    strength = Column(Numeric(3, 2), nullable=False)  # 0.00-1.00
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    parent_scenario = relationship("CounterfactualV2", foreign_keys=[parent_id], back_populates="relationships_as_parent")
    child_scenario = relationship("CounterfactualV2", foreign_keys=[child_id], back_populates="relationships_as_child")

    def __repr__(self):
        return f"<ScenarioRelationship(type={self.relationship_type}, strength={self.strength})>"


class Phase2CounterfactualLineage(Base):
    """
    Lineage tracking from Phase 2 fragilities to Phase 3 counterfactuals.
    Ensures full traceability across analysis phases.
    """
    __tablename__ = "phase2_counterfactual_lineage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fragility_id = Column(UUID(as_uuid=True), ForeignKey("fragility_points.id", ondelete="CASCADE"), nullable=False, index=True)
    counterfactual_id = Column(UUID(as_uuid=True), ForeignKey("counterfactuals_v2.id", ondelete="CASCADE"), nullable=False, index=True)

    contribution_score = Column(Numeric(3, 2))  # How much this fragility contributed (0-1)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    fragility = relationship("FragilityPoint")
    counterfactual = relationship("CounterfactualV2")

    def __repr__(self):
        return f"<Phase2CounterfactualLineage(fragility_id={self.fragility_id}, counterfactual_id={self.counterfactual_id})>"


class CounterfactualPortfolio(Base):
    """
    User-created portfolios for grouping related counterfactuals.
    Supports Phase 5 integration and strategic analysis.
    """
    __tablename__ = "counterfactual_portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text)
    counterfactual_ids = Column(JSONB, nullable=False)  # Array of UUID strings
    tags = Column(JSONB)  # User-defined tags

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    scenario = relationship("Scenario")

    def __repr__(self):
        return f"<CounterfactualPortfolio(id={self.id}, name={self.name})>"
# --- Fragility Analysis (Phase 3) ---
class FragilityAnalysis(Base):
    """
    Stores fragility evaluation for a given counterfactual.
    Holds a single summary score and a structured JSON breakdown.
    """
    __tablename__ = "fragility_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    counterfactual_id = Column(
        UUID(as_uuid=True),
        ForeignKey("counterfactuals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core results
    overall_score = Column(Numeric(5, 2), nullable=True)      # optional: 0–100.00 etc
    result = Column(JSON, nullable=False, default=dict)       # structured breakdown
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    counterfactual = relationship("Counterfactual", back_populates="fragility_analyses")

    def __repr__(self):
        return f"<FragilityAnalysis(id={self.id}, cf_id={self.counterfactual_id})>"

__all__ = [
    "CounterfactualAxis",
    "BreachCondition",
    "FragilityPoint",
    "CounterfactualV2",
    "ConsequenceChain",
    "ScenarioRelationship",
    "StrategicOutcome",
    "FragilityAnalysis",
]

