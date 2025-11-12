"""
Scenario and analysis models for multi-phase reasoning system.
"""
# Back-compat: re-export DependencyGraph so consumers can import it from models.scenario
from .dependency_graph import DependencyGraph  # noqa: F401

from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from models.database import Base

class Scenario(Base):
    """Scenario model for storing user input contexts."""

    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="scenarios")
    surface_analyses = relationship("SurfaceAnalysis", back_populates="scenario", cascade="all, delete-orphan")
    counterfactuals = relationship("Counterfactual", back_populates="scenario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scenario(id={self.id}, title={self.title})>"


class SurfaceAnalysis(Base):
    """Surface Analysis model for Phase 1: Assumption extraction."""

    __tablename__ = "surface_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    assumptions = Column(JSONB, nullable=False)  # Array of {id, text, category, confidence}
    baseline_narrative = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    scenario = relationship("Scenario", back_populates="surface_analyses")
    deep_questions = relationship("DeepQuestion", back_populates="surface_analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SurfaceAnalysis(id={self.id}, scenario_id={self.scenario_id})>"


class DeepQuestion(Base):
    """Deep Question model for Phase 2: Interrogative probing."""

    __tablename__ = "deep_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    surface_analysis_id = Column(UUID(as_uuid=True), ForeignKey("surface_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    assumption_id = Column(String(50), nullable=False)  # Reference into JSONB assumptions
    question_text = Column(Text, nullable=False)
    dimension = Column(String(50), nullable=False)  # temporal, structural, actor-based, resource-based, information
    user_response = Column(Text)
    relevance_score = Column(Integer)  # User rating 1-5
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    surface_analysis = relationship("SurfaceAnalysis", back_populates="deep_questions")

    def __repr__(self):
        return f"<DeepQuestion(id={self.id}, dimension={self.dimension})>"


class Counterfactual(Base):
    """Counterfactual model for Phase 3: Alternative scenario generation."""

    fragility_analyses = relationship(
    "FragilityAnalysis",
    back_populates="counterfactual",
    cascade="all, delete-orphan"
)
    
    __tablename__ = "counterfactuals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    axis = Column(String(50), nullable=False, index=True)  # One of 6 strategic axes
    breach_condition = Column(Text, nullable=False)
    consequences = Column(JSONB, nullable=False)  # Array of consequence objects
    severity_rating = Column(Integer)  # 1-10 scale
    probability_rating = Column(Numeric(3, 2))  # 0.00-1.00
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    scenario = relationship("Scenario", back_populates="counterfactuals")
    strategic_outcomes = relationship("StrategicOutcome", back_populates="counterfactual", cascade="all, delete-orphan")
    score = relationship("CounterfactualScore", back_populates="counterfactual", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Counterfactual(id={self.id}, axis={self.axis})>"


class StrategicOutcome(Base):
    """Strategic Outcome model for Phase 5: Trajectory projection."""

    __tablename__ = "strategic_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counterfactual_id = Column(UUID(as_uuid=True), ForeignKey("counterfactuals.id", ondelete="CASCADE"), nullable=False, index=True)
    trajectory = Column(JSONB, nullable=False)  # Timeline data structure
    decision_points = Column(JSONB)  # Critical decision moments
    inflection_points = Column(JSONB)  # Trajectory change points
    confidence_intervals = Column(JSONB)  # Confidence bounds over time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    counterfactual = relationship("Counterfactual", back_populates="strategic_outcomes")

    def __repr__(self):
        return f"<StrategicOutcome(id={self.id}, counterfactual_id={self.counterfactual_id})>"
        
# compatibility alias
CounterfactualV2 = Counterfactual
