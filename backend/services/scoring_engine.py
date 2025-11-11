"""
Multi-Factor Scoring Engine for Counterfactual Scenarios

This module implements severity and probability scoring algorithms
with confidence interval calculation using bootstrap resampling and
Monte Carlo simulation.
"""
import numpy as np
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from scipy import stats
import logging

logger = logging.getLogger(__name__)


@dataclass
class SeverityFactors:
    """Factors contributing to severity score (0-1 normalized)."""
    cascade_depth: float  # Number of consequence layers
    breadth_of_impact: float  # Number of domains affected
    deviation_magnitude: float  # Distance from baseline
    irreversibility: float  # Difficulty to reverse outcome

    def __post_init__(self):
        """Validate all factors are in [0, 1] range."""
        for field in ['cascade_depth', 'breadth_of_impact', 'deviation_magnitude', 'irreversibility']:
            value = getattr(self, field)
            if not 0 <= value <= 1:
                raise ValueError(f"{field} must be between 0 and 1, got {value}")


@dataclass
class ProbabilityFactors:
    """Factors contributing to probability score (0-1 normalized)."""
    fragility_strength: float  # Evidence strength of vulnerability
    historical_precedent: float  # Similar past events
    dependency_failures: float  # Required failures
    time_horizon: float  # Time distance adjustment

    def __post_init__(self):
        """Validate all factors are in [0, 1] range."""
        for field in ['fragility_strength', 'historical_precedent', 'dependency_failures', 'time_horizon']:
            value = getattr(self, field)
            if not 0 <= value <= 1:
                raise ValueError(f"{field} must be between 0 and 1, got {value}")


@dataclass
class ScoreResult:
    """Result of scoring calculation."""
    score: float  # Final score (0-1)
    confidence_interval: Tuple[float, float]  # (lower, upper) at 95% confidence
    factors: Dict[str, float]  # Individual factor contributions
    sensitivity: Dict[str, float]  # Factor influence scores


class ScoringEngine:
    """
    Multi-factor scoring engine for counterfactual scenarios.

    Calculates severity and probability scores using weighted factors
    with confidence intervals via bootstrap resampling and Monte Carlo.
    """

    # Default weights (can be overridden)
    DEFAULT_SEVERITY_WEIGHTS = {
        'cascade_depth': 0.30,
        'breadth_of_impact': 0.25,
        'deviation_magnitude': 0.25,
        'irreversibility': 0.20
    }

    DEFAULT_PROBABILITY_WEIGHTS = {
        'fragility_strength': 0.35,
        'historical_precedent': 0.30,
        'dependency_failures': 0.20,
        'time_horizon': 0.15
    }

    def __init__(
        self,
        severity_weights: Optional[Dict[str, float]] = None,
        probability_weights: Optional[Dict[str, float]] = None,
        confidence_level: float = 0.95,
        n_bootstrap_samples: int = 1000,
        random_seed: Optional[int] = None
    ):
        """
        Initialize scoring engine.

        Args:
            severity_weights: Custom weights for severity factors
            probability_weights: Custom weights for probability factors
            confidence_level: Confidence level for intervals (default 0.95)
            n_bootstrap_samples: Number of bootstrap iterations
            random_seed: Random seed for reproducibility
        """
        self.severity_weights = severity_weights or self.DEFAULT_SEVERITY_WEIGHTS
        self.probability_weights = probability_weights or self.DEFAULT_PROBABILITY_WEIGHTS
        self.confidence_level = confidence_level
        self.n_bootstrap_samples = n_bootstrap_samples

        # Validate weights sum to 1.0
        self._validate_weights(self.severity_weights, "severity")
        self._validate_weights(self.probability_weights, "probability")

        # Set random seed
        if random_seed is not None:
            np.random.seed(random_seed)

    def _validate_weights(self, weights: Dict[str, float], name: str):
        """Validate that weights sum to approximately 1.0."""
        total = sum(weights.values())
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"{name} weights must sum to 1.0, got {total}")

    def calculate_severity(self, factors: SeverityFactors) -> ScoreResult:
        """
        Calculate severity score with confidence interval.

        Args:
            factors: SeverityFactors instance with normalized values

        Returns:
            ScoreResult with score, CI, factors, and sensitivity
        """
        # Calculate base score
        score = sum(
            getattr(factors, factor) * weight
            for factor, weight in self.severity_weights.items()
        )

        # Calculate confidence interval using bootstrap
        ci = self._bootstrap_confidence_interval(factors, self.severity_weights)

        # Calculate sensitivity (which factors influence score most)
        sensitivity = self._calculate_sensitivity(factors, self.severity_weights)

        # Get individual factor contributions
        factor_contributions = {
            factor: getattr(factors, factor) * weight
            for factor, weight in self.severity_weights.items()
        }

        return ScoreResult(
            score=score,
            confidence_interval=ci,
            factors=factor_contributions,
            sensitivity=sensitivity
        )

    def calculate_probability(self, factors: ProbabilityFactors) -> ScoreResult:
        """
        Calculate probability score with confidence interval.

        Args:
            factors: ProbabilityFactors instance with normalized values

        Returns:
            ScoreResult with score, CI, factors, and sensitivity
        """
        # Calculate base score
        score = sum(
            getattr(factors, factor) * weight
            for factor, weight in self.probability_weights.items()
        )

        # Calculate confidence interval using bootstrap
        ci = self._bootstrap_confidence_interval(factors, self.probability_weights)

        # Calculate sensitivity
        sensitivity = self._calculate_sensitivity(factors, self.probability_weights)

        # Get individual factor contributions
        factor_contributions = {
            factor: getattr(factors, factor) * weight
            for factor, weight in self.probability_weights.items()
        }

        return ScoreResult(
            score=score,
            confidence_interval=ci,
            factors=factor_contributions,
            sensitivity=sensitivity
        )

    def _bootstrap_confidence_interval(
        self,
        factors: any,
        weights: Dict[str, float]
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval using bootstrap resampling.

        Adds noise to factor values and resamples to estimate uncertainty.
        """
        scores = []

        # Get factor values as array
        factor_values = np.array([getattr(factors, f) for f in weights.keys()])
        weight_values = np.array(list(weights.values()))

        # Bootstrap resampling with noise injection
        for _ in range(self.n_bootstrap_samples):
            # Add Gaussian noise (±5% std dev)
            noise = np.random.normal(0, 0.05, size=len(factor_values))
            perturbed_values = np.clip(factor_values + noise, 0, 1)

            # Calculate score with perturbed values
            score = np.dot(perturbed_values, weight_values)
            scores.append(score)

        # Calculate confidence interval
        alpha = 1 - self.confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        ci_lower = np.percentile(scores, lower_percentile)
        ci_upper = np.percentile(scores, upper_percentile)

        return (float(ci_lower), float(ci_upper))

    def _calculate_sensitivity(
        self,
        factors: any,
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate sensitivity of each factor (how much it influences final score).

        Uses partial derivative approximation: change in score for ±1% change in factor.
        """
        base_score = sum(
            getattr(factors, factor) * weight
            for factor, weight in weights.items()
        )

        sensitivity = {}
        delta = 0.01  # 1% change

        for factor, weight in weights.items():
            original_value = getattr(factors, factor)

            # Calculate score with +1% change
            perturbed_value = min(1.0, original_value + delta)
            score_increase = sum(
                (perturbed_value if f == factor else getattr(factors, f)) * weights[f]
                for f in weights.keys()
            )

            # Sensitivity is change in score per unit change in factor
            sensitivity[factor] = abs(score_increase - base_score) / delta

        return sensitivity

    def monte_carlo_simulation(
        self,
        severity_factors: SeverityFactors,
        probability_factors: ProbabilityFactors,
        n_simulations: int = 10000
    ) -> Dict[str, any]:
        """
        Run Monte Carlo simulation to estimate risk distribution.

        Args:
            severity_factors: Severity factors
            probability_factors: Probability factors
            n_simulations: Number of simulation runs

        Returns:
            Dictionary with simulation statistics
        """
        severity_scores = []
        probability_scores = []
        risk_scores = []  # severity × probability

        # Get factor arrays
        sev_values = np.array([getattr(severity_factors, f) for f in self.severity_weights.keys()])
        prob_values = np.array([getattr(probability_factors, f) for f in self.probability_weights.keys()])
        sev_weights = np.array(list(self.severity_weights.values()))
        prob_weights = np.array(list(self.probability_weights.values()))

        for _ in range(n_simulations):
            # Add noise to simulate uncertainty
            sev_noise = np.random.normal(0, 0.05, size=len(sev_values))
            prob_noise = np.random.normal(0, 0.05, size=len(prob_values))

            sev_perturbed = np.clip(sev_values + sev_noise, 0, 1)
            prob_perturbed = np.clip(prob_values + prob_noise, 0, 1)

            # Calculate scores
            sev_score = np.dot(sev_perturbed, sev_weights)
            prob_score = np.dot(prob_perturbed, prob_weights)
            risk_score = sev_score * prob_score

            severity_scores.append(sev_score)
            probability_scores.append(prob_score)
            risk_scores.append(risk_score)

        return {
            'severity': {
                'mean': float(np.mean(severity_scores)),
                'std': float(np.std(severity_scores)),
                'percentiles': {
                    'p5': float(np.percentile(severity_scores, 5)),
                    'p25': float(np.percentile(severity_scores, 25)),
                    'p50': float(np.percentile(severity_scores, 50)),
                    'p75': float(np.percentile(severity_scores, 75)),
                    'p95': float(np.percentile(severity_scores, 95))
                }
            },
            'probability': {
                'mean': float(np.mean(probability_scores)),
                'std': float(np.std(probability_scores)),
                'percentiles': {
                    'p5': float(np.percentile(probability_scores, 5)),
                    'p25': float(np.percentile(probability_scores, 25)),
                    'p50': float(np.percentile(probability_scores, 50)),
                    'p75': float(np.percentile(probability_scores, 75)),
                    'p95': float(np.percentile(probability_scores, 95))
                }
            },
            'risk': {
                'mean': float(np.mean(risk_scores)),
                'std': float(np.std(risk_scores)),
                'percentiles': {
                    'p5': float(np.percentile(risk_scores, 5)),
                    'p25': float(np.percentile(risk_scores, 25)),
                    'p50': float(np.percentile(risk_scores, 50)),
                    'p75': float(np.percentile(risk_scores, 75)),
                    'p95': float(np.percentile(risk_scores, 95))
                }
            }
        }


class CalibrationEngine:
    """
    Human-in-the-loop calibration engine for expert score adjustments.

    Learns from expert adjustments to improve future scoring accuracy.
    """

    def __init__(self):
        """Initialize calibration engine."""
        self.adjustments: List[Dict] = []

    def record_adjustment(
        self,
        counterfactual_id: str,
        original_severity: float,
        adjusted_severity: float,
        original_probability: float,
        adjusted_probability: float,
        expert_rationale: Optional[str] = None
    ):
        """
        Record an expert adjustment for learning.

        Args:
            counterfactual_id: ID of adjusted counterfactual
            original_severity: Original algorithm score
            adjusted_severity: Expert-adjusted score
            original_probability: Original algorithm score
            adjusted_probability: Expert-adjusted score
            expert_rationale: Optional explanation
        """
        adjustment = {
            'counterfactual_id': counterfactual_id,
            'severity_delta': adjusted_severity - original_severity,
            'probability_delta': adjusted_probability - original_probability,
            'rationale': expert_rationale,
            'timestamp': np.datetime64('now')
        }
        self.adjustments.append(adjustment)

        logger.info(
            f"Recorded adjustment for {counterfactual_id}: "
            f"severity Δ={adjustment['severity_delta']:.3f}, "
            f"probability Δ={adjustment['probability_delta']:.3f}"
        )

    def get_adjustment_statistics(self) -> Dict[str, any]:
        """
        Get statistics on expert adjustments for learning.

        Returns:
            Dictionary with adjustment patterns
        """
        if not self.adjustments:
            return {'message': 'No adjustments recorded yet'}

        severity_deltas = [adj['severity_delta'] for adj in self.adjustments]
        probability_deltas = [adj['probability_delta'] for adj in self.adjustments]

        return {
            'total_adjustments': len(self.adjustments),
            'severity_bias': {
                'mean_adjustment': float(np.mean(severity_deltas)),
                'std': float(np.std(severity_deltas)),
                'tendency': 'overestimate' if np.mean(severity_deltas) < 0 else 'underestimate'
            },
            'probability_bias': {
                'mean_adjustment': float(np.mean(probability_deltas)),
                'std': float(np.std(probability_deltas)),
                'tendency': 'overestimate' if np.mean(probability_deltas) < 0 else 'underestimate'
            }
        }

    def suggest_weight_corrections(
        self,
        scoring_engine: ScoringEngine
    ) -> Dict[str, Dict[str, float]]:
        """
        Suggest weight corrections based on adjustment patterns.

        Args:
            scoring_engine: Current scoring engine instance

        Returns:
            Suggested weight adjustments
        """
        if len(self.adjustments) < 10:
            return {'message': 'Need at least 10 adjustments for weight suggestions'}

        # Placeholder for learning algorithm
        # In production, this would use regression or ML to correlate
        # adjustments with factor patterns

        stats = self.get_adjustment_statistics()

        return {
            'severity_weights': {
                'current': scoring_engine.severity_weights,
                'suggested_adjustment': 'Increase if underestimating, decrease if overestimating',
                'bias': stats['severity_bias']['tendency']
            },
            'probability_weights': {
                'current': scoring_engine.probability_weights,
                'suggested_adjustment': 'Increase if underestimating, decrease if overestimating',
                'bias': stats['probability_bias']['tendency']
            }
        }


# Utility functions for factor extraction from counterfactuals
def extract_severity_factors_from_counterfactual(counterfactual_data: Dict) -> SeverityFactors:
    """
    Extract severity factors from counterfactual data.

    Args:
        counterfactual_data: Dictionary with counterfactual attributes

    Returns:
        SeverityFactors instance
    """
    # Extract consequence chain depth
    consequences = counterfactual_data.get('consequences', [])
    max_depth = 5  # Normalize by max expected depth
    cascade_depth = min(len(consequences), max_depth) / max_depth

    # Extract domains affected
    domains = set()
    for cons in consequences:
        domains.update(cons.get('domains', []))
    max_domains = 6  # Political, economic, military, social, tech, environmental
    breadth_of_impact = min(len(domains), max_domains) / max_domains

    # Extract deviation magnitude (how far from baseline)
    severity_rating = counterfactual_data.get('estimated_severity', 0.5)  # 0-1 scale
    deviation_magnitude = severity_rating

    # Extract irreversibility indicators
    irreversibility_keywords = ['permanent', 'irreversible', 'structural', 'fundamental']
    description = counterfactual_data.get('description', '').lower()
    irreversibility = sum(1 for kw in irreversibility_keywords if kw in description) / len(irreversibility_keywords)

    return SeverityFactors(
        cascade_depth=cascade_depth,
        breadth_of_impact=breadth_of_impact,
        deviation_magnitude=deviation_magnitude,
        irreversibility=irreversibility
    )


def extract_probability_factors_from_counterfactual(counterfactual_data: Dict) -> ProbabilityFactors:
    """
    Extract probability factors from counterfactual data.

    Args:
        counterfactual_data: Dictionary with counterfactual attributes

    Returns:
        ProbabilityFactors instance
    """
    # Extract fragility strength
    fragility_score = counterfactual_data.get('fragility_evidence_score', 0.5)
    fragility_strength = fragility_score

    # Extract historical precedent
    has_precedent = counterfactual_data.get('historical_precedent', False)
    precedent_count = counterfactual_data.get('precedent_count', 0)
    historical_precedent = min(precedent_count / 3, 1.0) if has_precedent else 0.2

    # Extract dependency failures needed
    breach_conditions = counterfactual_data.get('breach_conditions', [])
    max_dependencies = 5
    # Fewer dependencies = higher probability
    dependency_failures = 1.0 - (min(len(breach_conditions), max_dependencies) / max_dependencies)

    # Extract time horizon (nearer = more probable)
    time_horizon_str = counterfactual_data.get('time_horizon', 'medium')
    time_horizon_map = {
        'immediate': 0.9,
        'short': 0.7,
        'medium': 0.5,
        'long': 0.3,
        'very_long': 0.1
    }
    time_horizon = time_horizon_map.get(time_horizon_str, 0.5)

    return ProbabilityFactors(
        fragility_strength=fragility_strength,
        historical_precedent=historical_precedent,
        dependency_failures=dependency_failures,
        time_horizon=time_horizon
    )
