"""
Advanced Prompt Management System with Versioning and A/B Testing
Enables systematic prompt optimization and quality tracking
"""
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import random


@dataclass
class PromptVersion:
    """A versioned prompt with performance metrics"""
    name: str
    version: str
    template: str
    description: str
    created_at: str
    performance_metrics: Dict[str, float]
    is_active: bool = True
    test_group_percentage: float = 0.0  # For A/B testing


@dataclass
class PromptEvaluation:
    """Evaluation result for a prompt execution"""
    prompt_name: str
    prompt_version: str
    execution_id: str
    timestamp: str
    metrics: Dict[str, float]
    user_feedback: Optional[Dict[str, Any]] = None


class PromptRegistry:
    """Manages prompt versions and performance tracking"""

    def __init__(self, storage_path: str = "/Users/raminhedayatpour/Documents/VibeProjects/test/backend/data/prompts"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.prompts: Dict[str, List[PromptVersion]] = {}
        self.evaluations: List[PromptEvaluation] = []
        self._load_prompts()

    def _load_prompts(self):
        """Load prompts from disk"""
        registry_file = self.storage_path / "registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                data = json.load(f)
                for prompt_name, versions in data.items():
                    self.prompts[prompt_name] = [
                        PromptVersion(**v) for v in versions
                    ]

    def _save_prompts(self):
        """Save prompts to disk"""
        registry_file = self.storage_path / "registry.json"
        data = {}
        for prompt_name, versions in self.prompts.items():
            data[prompt_name] = [asdict(v) for v in versions]

        with open(registry_file, 'w') as f:
            json.dump(data, f, indent=2)

    def register_prompt(
        self,
        name: str,
        version: str,
        template: str,
        description: str,
        is_active: bool = True,
        test_group_percentage: float = 0.0
    ):
        """Register a new prompt version"""
        if name not in self.prompts:
            self.prompts[name] = []

        prompt_version = PromptVersion(
            name=name,
            version=version,
            template=template,
            description=description,
            created_at=datetime.now().isoformat(),
            performance_metrics={},
            is_active=is_active,
            test_group_percentage=test_group_percentage
        )

        self.prompts[name].append(prompt_version)
        self._save_prompts()
        print(f"✅ Registered {name} v{version}")

    def get_prompt(
        self,
        name: str,
        version: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> PromptVersion:
        """
        Get a prompt version
        If version is None, returns based on A/B testing logic
        """
        if name not in self.prompts:
            raise ValueError(f"Unknown prompt: {name}")

        versions = self.prompts[name]
        active_versions = [v for v in versions if v.is_active]

        if not active_versions:
            raise ValueError(f"No active versions for {name}")

        # Specific version requested
        if version:
            for v in active_versions:
                if v.version == version:
                    return v
            raise ValueError(f"Version {version} not found for {name}")

        # A/B testing logic
        return self._ab_test_selection(name, active_versions, user_id)

    def _ab_test_selection(
        self,
        name: str,
        versions: List[PromptVersion],
        user_id: Optional[str]
    ) -> PromptVersion:
        """Select prompt version using A/B testing logic"""
        # If only one version, return it
        if len(versions) == 1:
            return versions[0]

        # Deterministic selection based on user_id for consistent experience
        if user_id:
            hash_val = int(hashlib.sha256(f"{name}:{user_id}".encode()).hexdigest(), 16)
            selector = (hash_val % 100) / 100.0
        else:
            selector = random.random()

        # Sort versions by test_group_percentage for cumulative selection
        sorted_versions = sorted(versions, key=lambda v: v.test_group_percentage)

        cumulative = 0.0
        for version in sorted_versions:
            cumulative += version.test_group_percentage
            if selector <= cumulative:
                return version

        # Default to last version if percentages don't sum to 1.0
        return sorted_versions[-1]

    def evaluate_quality(
        self,
        prompt_name: str,
        prompt_version: str,
        output: Any,
        ground_truth: Optional[Any] = None
    ) -> PromptEvaluation:
        """
        Evaluate prompt output quality using automated metrics
        Can also use LLM-as-judge for subjective quality
        """
        execution_id = hashlib.sha256(
            f"{prompt_name}:{prompt_version}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        metrics = {}

        # Phase-specific evaluation
        if "assumption" in prompt_name.lower():
            metrics = self._evaluate_assumptions(output, ground_truth)
        elif "question" in prompt_name.lower():
            metrics = self._evaluate_questions(output, ground_truth)
        elif "counterfactual" in prompt_name.lower():
            metrics = self._evaluate_counterfactuals(output, ground_truth)

        evaluation = PromptEvaluation(
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            execution_id=execution_id,
            timestamp=datetime.now().isoformat(),
            metrics=metrics
        )

        self.evaluations.append(evaluation)
        self._update_performance_metrics(prompt_name, prompt_version, metrics)

        return evaluation

    def _evaluate_assumptions(self, output: List[Dict], ground_truth: Optional[List[Dict]]) -> Dict[str, float]:
        """Evaluate assumption extraction quality"""
        metrics = {
            'count': len(output),
            'avg_confidence': sum(a.get('confidence', 0) for a in output) / max(len(output), 1),
            'has_categories': sum(1 for a in output if 'category' in a) / max(len(output), 1),
            'avg_length': sum(len(a.get('text', '').split()) for a in output) / max(len(output), 1)
        }

        # If ground truth available, calculate precision/recall
        if ground_truth:
            # Simplified - would need semantic matching in production
            metrics['ground_truth_coverage'] = min(len(output) / max(len(ground_truth), 1), 1.0)

        return metrics

    def _evaluate_questions(self, output: List[Dict], ground_truth: Optional[List[Dict]]) -> Dict[str, float]:
        """Evaluate question generation quality"""
        metrics = {
            'count': len(output),
            'dimension_coverage': len(set(q.get('dimension', '') for q in output)),
            'avg_length': sum(len(q.get('question_text', '').split()) for q in output) / max(len(output), 1),
            'has_assumption_links': sum(1 for q in output if 'assumption_id' in q) / max(len(output), 1)
        }

        # Check for deep probing indicators
        deep_indicators = ['why', 'how', 'what if', 'under what conditions']
        deep_count = sum(
            1 for q in output
            if any(ind in q.get('question_text', '').lower() for ind in deep_indicators)
        )
        metrics['deep_probing_rate'] = deep_count / max(len(output), 1)

        return metrics

    def _evaluate_counterfactuals(self, output: List[Dict], ground_truth: Optional[List[Dict]]) -> Dict[str, float]:
        """Evaluate counterfactual quality"""
        metrics = {
            'count': len(output),
            'axis_coverage': len(set(cf.get('axis', '') for cf in output)),
            'avg_consequences': sum(len(cf.get('consequences', [])) for cf in output) / max(len(output), 1),
            'avg_severity': sum(cf.get('severity_rating', 0) for cf in output) / max(len(output), 1),
            'avg_probability': sum(cf.get('probability_rating', 0) for cf in output) / max(len(output), 1)
        }

        # Check breach condition specificity
        specific_breaches = sum(
            1 for cf in output
            if len(cf.get('breach_condition', '').split()) >= 10
        )
        metrics['specificity_rate'] = specific_breaches / max(len(output), 1)

        return metrics

    def _update_performance_metrics(self, prompt_name: str, version: str, new_metrics: Dict[str, float]):
        """Update rolling average of performance metrics"""
        for prompt_version in self.prompts.get(prompt_name, []):
            if prompt_version.version == version:
                # Rolling average (exponential moving average)
                alpha = 0.3  # Weight for new observation
                for metric_name, new_value in new_metrics.items():
                    if metric_name in prompt_version.performance_metrics:
                        old_value = prompt_version.performance_metrics[metric_name]
                        prompt_version.performance_metrics[metric_name] = \
                            alpha * new_value + (1 - alpha) * old_value
                    else:
                        prompt_version.performance_metrics[metric_name] = new_value

                self._save_prompts()
                break

    def get_performance_report(self, prompt_name: str) -> Dict:
        """Generate performance comparison report across versions"""
        if prompt_name not in self.prompts:
            return {'error': f'Prompt {prompt_name} not found'}

        versions = self.prompts[prompt_name]
        report = {
            'prompt_name': prompt_name,
            'versions': []
        }

        for version in versions:
            version_report = {
                'version': version.version,
                'is_active': version.is_active,
                'created_at': version.created_at,
                'description': version.description,
                'metrics': version.performance_metrics,
                'test_group_percentage': version.test_group_percentage
            }
            report['versions'].append(version_report)

        # Add comparison statistics
        if len(versions) > 1:
            report['comparison'] = self._compare_versions(versions)

        return report

    def _compare_versions(self, versions: List[PromptVersion]) -> Dict:
        """Compare performance across versions"""
        comparison = {}

        # Get all metric names
        all_metrics = set()
        for v in versions:
            all_metrics.update(v.performance_metrics.keys())

        for metric in all_metrics:
            values = [
                v.performance_metrics.get(metric, 0)
                for v in versions
            ]
            comparison[metric] = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'improvement_pct': ((max(values) - min(values)) / max(min(values), 0.001)) * 100
            }

        return comparison

    def export_evaluations(self, output_file: str):
        """Export all evaluations for analysis"""
        data = [asdict(e) for e in self.evaluations]
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Exported {len(data)} evaluations to {output_file}")


# Initialize improved prompts (v2.0)
IMPROVED_PROMPTS = {
    'assumption_extraction_v2': {
        'version': '2.0.0',
        'description': 'Improved with explicit examples and stricter output format',
        'template': """Analyze the following scenario and extract the key assumptions underlying it. Focus on identifying both explicit and implicit assumptions that form the foundation of the scenario's baseline narrative.

Scenario:
{scenario}

INSTRUCTIONS:
1. Identify 8-15 key assumptions (not more, not fewer)
2. For each assumption:
   - State it clearly as a declarative sentence
   - Classify into ONE category: political, economic, technological, social, operational, or strategic
   - Assign a confidence level (0.0-1.0) based on how central it is to the scenario

QUALITY CRITERIA:
- Be specific, not vague (avoid "might", "could", "possibly")
- Focus on assumptions that, if violated, would significantly alter the scenario
- Include quantifiable elements where possible (percentages, timeframes, amounts)

EXAMPLE OUTPUT FORMAT:
{{
    "assumptions": [
        {{
            "id": "assumption_1",
            "text": "Markets will maintain liquidity with at least $2B daily trading volume",
            "category": "economic",
            "confidence": 0.85,
            "supporting_evidence": "Historical trading patterns show consistent volume"
        }},
        {{
            "id": "assumption_2",
            "text": "Diplomatic channels between parties will remain open for at least 6 months",
            "category": "political",
            "confidence": 0.65,
            "supporting_evidence": "Recent diplomatic engagement history"
        }}
    ]
}}

Return ONLY valid JSON matching this structure."""
    },

    'probing_questions_v2': {
        'version': '2.0.0',
        'description': 'Enhanced with specific dimension focus and consequence exploration',
        'template': """Generate deep, probing questions to expose hidden fragilities in these assumptions.

Assumptions:
{assumptions}

INSTRUCTIONS:
Generate 12-20 questions total, distributed across these 5 dimensions:

1. **Temporal Dimension** (3-4 questions):
   - What if timelines compress or extend dramatically?
   - What if events happen in a different sequence?
   - What if critical windows close earlier than expected?

2. **Structural Dimension** (3-4 questions):
   - What dependencies are load-bearing?
   - What if key structural relationships break?
   - What single points of failure exist?

3. **Actor-Based Dimension** (3-4 questions):
   - Whose incentives could shift unexpectedly?
   - What if key actors behave irrationally?
   - What if coalitions fracture?

4. **Resource Dimension** (3-4 questions):
   - What constraints could suddenly bind?
   - What if resource assumptions fail by 50%+?
   - What alternative resource paths exist?

5. **Information Dimension** (2-4 questions):
   - What unknowns could surface and change everything?
   - What if key information is wrong?
   - What if information asymmetries reverse?

QUALITY CRITERIA:
- Each question must challenge a specific assumption
- Questions should start with "What if", "How", or "Why"
- Questions should imply potential consequences
- Avoid generic questions that could apply to any scenario

EXAMPLE:
Instead of: "What if the timeline changes?"
Better: "What if diplomatic negotiations collapse within 2 weeks instead of the assumed 6-month window, before economic sanctions take effect?"

Return as JSON:
{{
    "questions": [
        {{
            "assumption_id": "assumption_1",
            "question_text": "What if market liquidity drops below $500M daily due to coordinated withdrawal, triggering circuit breakers?",
            "dimension": "resource",
            "implied_consequence": "Trading halts could cascade across interconnected markets",
            "severity_if_true": 8
        }}
    ]
}}"""
    },

    'counterfactual_v2': {
        'version': '2.0.0',
        'description': 'Improved with stricter axis definitions and consequence chains',
        'template': """Generate counterfactual scenarios by forcing specific assumption breaches and mapping consequences.

Original Scenario:
{scenario}

Assumptions:
{assumptions}

Vulnerabilities Identified:
{vulnerabilities}

INSTRUCTIONS:
Generate 6-12 counterfactual scenarios across these SIX STRATEGIC AXES (at least 1 per axis):

1. **Geopolitical Alignment Shifts**: Alliances break or form unexpectedly
2. **Economic Constraint Breaches**: Financial assumptions fail (funding dries up, costs explode)
3. **Technological Disruption**: Tech changes faster/slower than expected or fails
4. **Actor Strategy Changes**: Key players pivot strategies or goals
5. **Information Environment Shifts**: Truth reveals, lies spread, narrative control lost
6. **Resource Availability Changes**: Critical resources (people, materials, access) constrained or abundant

QUALITY CRITERIA:
- Breach condition must be specific (not "markets crash" but "S&P 500 drops 25% in 3 days due to X")
- Consequences must form a logical chain (first-order → second-order → third-order)
- Each consequence must have severity (1-10) and timeframe
- Severity and probability ratings must be realistic (avoid extremes unless justified)

EXAMPLE:
{{
    "counterfactuals": [
        {{
            "axis": "economic_constraint",
            "breach_condition": "Federal Reserve raises rates by 200 basis points in emergency meeting, citing inflation at 8.5% instead of expected 3%",
            "consequences": [
                {{
                    "description": "Mortgage rates jump from 6% to 8.5% overnight",
                    "severity": 7,
                    "timeframe": "immediate",
                    "affected_parties": ["homebuyers", "real estate sector"]
                }},
                {{
                    "description": "Housing starts drop 40% as buyers withdraw from market",
                    "severity": 8,
                    "timeframe": "1-2 months",
                    "affected_parties": ["construction industry", "suppliers"]
                }},
                {{
                    "description": "Regional banks with heavy real estate exposure face liquidity crisis",
                    "severity": 9,
                    "timeframe": "3-6 months",
                    "affected_parties": ["regional banks", "depositors", "FDIC"]
                }}
            ],
            "severity_rating": 8,
            "probability_rating": 0.15,
            "rationale": "Fed has historically acted aggressively when inflation exceeds 7%"
        }}
    ]
}}"""
    }
}


def initialize_prompt_registry():
    """Initialize prompt registry with v1 and v2 prompts"""
    registry = PromptRegistry()

    # Register improved prompts
    for prompt_name, config in IMPROVED_PROMPTS.items():
        registry.register_prompt(
            name=prompt_name.replace('_v2', ''),
            version=config['version'],
            template=config['template'],
            description=config['description'],
            is_active=True,
            test_group_percentage=0.5  # 50% A/B test split
        )

    return registry


if __name__ == "__main__":
    # Example usage
    registry = initialize_prompt_registry()
    print("\n📊 Prompt Registry Initialized")

    # Get performance report
    report = registry.get_performance_report('assumption_extraction')
    print(json.dumps(report, indent=2))
