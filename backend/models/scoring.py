"""
SQLAlchemy models for counterfactual scoring system.
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.database import Base


class CounterfactualScore(Base):
    """
    Stores calculated scores for counterfactual scenarios.

    Includes severity, probability, confidence intervals, and calibration data.
    """
    __tablename__ = "counterfactual_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counterfactual_id = Column(UUID(as_uuid=True), ForeignKey('counterfactuals.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Severity scoring
    severity_score = Column(Numeric(4, 3), nullable=False)  # 0.000 to 1.000
    severity_ci_lower = Column(Numeric(4, 3), nullable=False)
    severity_ci_upper = Column(Numeric(4, 3), nullable=False)

    # Severity factor contributions
    severity_cascade_depth = Column(Numeric(4, 3))
    severity_breadth_of_impact = Column(Numeric(4, 3))
    severity_deviation_magnitude = Column(Numeric(4, 3))
    severity_irreversibility = Column(Numeric(4, 3))

    # Probability scoring
    probability_score = Column(Numeric(4, 3), nullable=False)  # 0.000 to 1.000
    probability_ci_lower = Column(Numeric(4, 3), nullable=False)
    probability_ci_upper = Column(Numeric(4, 3), nullable=False)

    # Probability factor contributions
    probability_fragility_strength = Column(Numeric(4, 3))
    probability_historical_precedent = Column(Numeric(4, 3))
    probability_dependency_failures = Column(Numeric(4, 3))
    probability_time_horizon = Column(Numeric(4, 3))

    # Risk score (severity × probability)
    risk_score = Column(Numeric(4, 3))

    # Sensitivity analysis (JSON)
    severity_sensitivity = Column(JSON)  # Which factors influence most
    probability_sensitivity = Column(JSON)

    # Metadata
    confidence_level = Column(Numeric(3, 2), default=0.95)  # 0.95 = 95%
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    algorithm_version = Column(String(20), default="1.0.0")

    # Calibration (expert adjustments)
    is_calibrated = Column(Boolean, default=False)
    calibrated_severity = Column(Numeric(4, 3))
    calibrated_probability = Column(Numeric(4, 3))
    calibrated_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    calibration_timestamp = Column(DateTime)
    calibration_rationale = Column(Text)

    # Weights used for calculation (JSON)
    severity_weights = Column(JSON)
    probability_weights = Column(JSON)

    # Relationships
    counterfactual = relationship("Counterfactual", back_populates="score")
    calibrated_by = relationship("User")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': str(self.id),
            'counterfactual_id': str(self.counterfactual_id),
            'severity': {
                'score': float(self.severity_score),
                'confidence_interval': [float(self.severity_ci_lower), float(self.severity_ci_upper)],
                'factors': {
                    'cascade_depth': float(self.severity_cascade_depth) if self.severity_cascade_depth else None,
                    'breadth_of_impact': float(self.severity_breadth_of_impact) if self.severity_breadth_of_impact else None,
                    'deviation_magnitude': float(self.severity_deviation_magnitude) if self.severity_deviation_magnitude else None,
                    'irreversibility': float(self.severity_irreversibility) if self.severity_irreversibility else None
                },
                'sensitivity': self.severity_sensitivity
            },
            'probability': {
                'score': float(self.probability_score),
                'confidence_interval': [float(self.probability_ci_lower), float(self.probability_ci_upper)],
                'factors': {
                    'fragility_strength': float(self.probability_fragility_strength) if self.probability_fragility_strength else None,
                    'historical_precedent': float(self.probability_historical_precedent) if self.probability_historical_precedent else None,
                    'dependency_failures': float(self.probability_dependency_failures) if self.probability_dependency_failures else None,
                    'time_horizon': float(self.probability_time_horizon) if self.probability_time_horizon else None
                },
                'sensitivity': self.probability_sensitivity
            },
            'risk_score': float(self.risk_score) if self.risk_score else None,
            'calibration': {
                'is_calibrated': self.is_calibrated,
                'severity': float(self.calibrated_severity) if self.calibrated_severity else None,
                'probability': float(self.calibrated_probability) if self.calibrated_probability else None,
                'rationale': self.calibration_rationale,
                'timestamp': self.calibration_timestamp.isoformat() if self.calibration_timestamp else None,
                'calibrated_by': str(self.calibrated_by_user_id) if self.calibrated_by_user_id else None
            },
            'metadata': {
                'confidence_level': float(self.confidence_level),
                'computed_at': self.computed_at.isoformat(),
                'algorithm_version': self.algorithm_version,
                'severity_weights': self.severity_weights,
                'probability_weights': self.probability_weights
            }
        }


class ScoringAdjustment(Base):
    """
    Historical record of expert adjustments for learning.
    """
    __tablename__ = "scoring_adjustments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    score_id = Column(UUID(as_uuid=True), ForeignKey('counterfactual_scores.id', ondelete='CASCADE'), nullable=False)

    # Original scores
    original_severity = Column(Numeric(4, 3), nullable=False)
    original_probability = Column(Numeric(4, 3), nullable=False)

    # Adjusted scores
    adjusted_severity = Column(Numeric(4, 3), nullable=False)
    adjusted_probability = Column(Numeric(4, 3), nullable=False)

    # Deltas
    severity_delta = Column(Numeric(4, 3))
    probability_delta = Column(Numeric(4, 3))

    # Adjustment metadata
    adjusted_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    adjustment_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    rationale = Column(Text)

    # Context
    counterfactual_context = Column(JSON)  # Snapshot of counterfactual at adjustment time

    # Relationships
    score = relationship("CounterfactualScore")
    adjusted_by = relationship("User")

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': str(self.id),
            'score_id': str(self.score_id),
            'original': {
                'severity': float(self.original_severity),
                'probability': float(self.original_probability)
            },
            'adjusted': {
                'severity': float(self.adjusted_severity),
                'probability': float(self.adjusted_probability)
            },
            'delta': {
                'severity': float(self.severity_delta),
                'probability': float(self.probability_delta)
            },
            'adjusted_by': str(self.adjusted_by_user_id),
            'timestamp': self.adjustment_timestamp.isoformat(),
            'rationale': self.rationale
        }
