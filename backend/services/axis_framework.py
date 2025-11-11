"""
Six-Axis Counterfactual Framework Definition
Sprint 4 - Task 1: Strategic Axes

Defines the six strategic dimensions for counterfactual scenario generation.
Each axis represents a fundamental way assumptions can fail or diverge.
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class StrategicAxis:
    """Definition of a strategic axis for counterfactual generation."""
    id: str
    name: str
    description: str
    prompt_template: str
    focus_areas: List[str]
    example_breaches: List[str]


# Six Strategic Axes for Counterfactual Generation
STRATEGIC_AXES: Dict[str, StrategicAxis] = {
    "temporal_shifts": StrategicAxis(
        id="temporal_shifts",
        name="Temporal Shifts",
        description=(
            "Explores how timeline changes affect scenario outcomes. "
            "Examines acceleration, delays, event reordering, and timing mismatches. "
            "Tests assumptions about critical windows, decision deadlines, and sequence dependencies."
        ),
        prompt_template=(
            "Given the fragility: {fragility_description}\n\n"
            "Generate a breach condition that involves timeline changes:\n"
            "- What if a critical event is accelerated by {duration}?\n"
            "- What if a key decision deadline is compressed or extended?\n"
            "- What if events occur out of expected sequence?\n"
            "- What if parallel processes desynchronize?\n\n"
            "Create a specific, observable trigger event that would invalidate "
            "timeline assumptions and explain the cascading consequences."
        ),
        focus_areas=[
            "Timeline acceleration/delays",
            "Event sequence disruption",
            "Critical window compression",
            "Decision deadline shifts",
            "Synchronization failures",
            "Buffer exhaustion"
        ],
        example_breaches=[
            "Military mobilization accelerates by 6 months, catching diplomatic efforts unprepared",
            "Regulatory approval delayed by 2 years, missing market window",
            "Cascading supply chain delays compress decision window to 48 hours",
            "Technology development occurs 5 years earlier than baseline assumption"
        ]
    ),

    "actor_behavior": StrategicAxis(
        id="actor_behavior",
        name="Actor Behavior Changes",
        description=(
            "Explores how changes in actor motivations, capabilities, or strategies alter outcomes. "
            "Examines incentive shifts, alliance breakdowns, capability gaps, and strategic pivots. "
            "Tests assumptions about rationality, competence, and intent."
        ),
        prompt_template=(
            "Given the fragility: {fragility_description}\n\n"
            "Generate a breach condition involving actor behavior changes:\n"
            "- What if a key actor changes their motivation or strategy?\n"
            "- What if an alliance breaks down unexpectedly?\n"
            "- What if actor capabilities are overestimated or underestimated?\n"
            "- What if previously aligned incentives diverge?\n\n"
            "Create a specific trigger involving actor decisions or behaviors that "
            "would invalidate baseline assumptions about how actors will act."
        ),
        focus_areas=[
            "Motivation changes",
            "Capability shifts",
            "Alliance breakdowns",
            "Strategic pivots",
            "Incentive misalignment",
            "Competence gaps",
            "Leadership changes",
            "Trust erosion"
        ],
        example_breaches=[
            "Allied nation switches position due to domestic political pressure",
            "CEO replacement leads to complete strategic reversal",
            "Assumed technical capability proves non-existent under stress",
            "Short-term incentives override long-term commitments",
            "Key actor proves irrational or ideologically driven"
        ]
    ),

    "resource_constraints": StrategicAxis(
        id="resource_constraints",
        name="Resource Constraint Changes",
        description=(
            "Explores how changes in resource availability, allocation, or access impact scenarios. "
            "Examines supply disruptions, budget constraints, substitution failures, and competition. "
            "Tests assumptions about resource abundance, elasticity, and fungibility."
        ),
        prompt_template=(
            "Given the fragility: {fragility_description}\n\n"
            "Generate a breach condition involving resource constraints:\n"
            "- What if a critical resource becomes scarce or unavailable?\n"
            "- What if budget or funding is cut significantly?\n"
            "- What if substitutes prove inadequate?\n"
            "- What if competition for resources intensifies?\n\n"
            "Create a specific trigger involving resource availability that would "
            "invalidate baseline assumptions about having sufficient resources."
        ),
        focus_areas=[
            "Supply disruptions",
            "Budget cuts",
            "Access limitations",
            "Substitution failures",
            "Competition intensification",
            "Allocation conflicts",
            "Capacity constraints",
            "Cost escalation"
        ],
        example_breaches=[
            "Critical semiconductor supply drops 60% due to geopolitical conflict",
            "Budget slashed 40% mid-program, forcing capability compromises",
            "Alternative suppliers prove technically incompatible",
            "Three simultaneous crises compete for same limited resources",
            "Energy costs triple, making operations economically unviable"
        ]
    ),

    "structural_failures": StrategicAxis(
        id="structural_failures",
        name="Structural/Institutional Failures",
        description=(
            "Explores how system breakdowns, institutional collapses, or rule changes impact scenarios. "
            "Examines single points of failure, cascade effects, regulatory shifts, and governance breakdowns. "
            "Tests assumptions about system resilience, institutional stability, and structural integrity."
        ),
        prompt_template=(
            "Given the fragility: {fragility_description}\n\n"
            "Generate a breach condition involving structural or institutional failure:\n"
            "- What if a critical system component fails completely?\n"
            "- What if institutional authority breaks down?\n"
            "- What if regulatory frameworks change dramatically?\n"
            "- What if cascading failures overwhelm redundancy?\n\n"
            "Create a specific trigger involving system or institutional collapse that "
            "would invalidate baseline assumptions about structural stability."
        ),
        focus_areas=[
            "Single point of failure",
            "Cascade failures",
            "Institutional collapse",
            "Regulatory changes",
            "System overload",
            "Redundancy exhaustion",
            "Coordination breakdown",
            "Governance failure"
        ],
        example_breaches=[
            "Central clearing system failure paralyzes financial markets",
            "Supreme Court ruling invalidates entire regulatory framework",
            "Three simultaneous infrastructure failures exhaust emergency capacity",
            "International institution loses legitimacy, treaties unravel",
            "Digital backbone compromised, critical systems offline for weeks"
        ]
    ),

    "information_asymmetry": StrategicAxis(
        id="information_asymmetry",
        name="Information Asymmetry Changes",
        description=(
            "Explores how changes in information availability, accuracy, or distribution affect outcomes. "
            "Examines intelligence gaps, deception, transparency shifts, and surveillance changes. "
            "Tests assumptions about what is knowable, when it is known, and who knows it."
        ),
        prompt_template=(
            "Given the fragility: {fragility_description}\n\n"
            "Generate a breach condition involving information changes:\n"
            "- What if critical intelligence is unavailable, wrong, or delayed?\n"
            "- What if adversaries have more information than assumed?\n"
            "- What if transparency suddenly increases or decreases?\n"
            "- What if deception is more sophisticated than anticipated?\n\n"
            "Create a specific trigger involving information availability or accuracy "
            "that would invalidate baseline assumptions about what is known."
        ),
        focus_areas=[
            "Intelligence gaps",
            "Deception/misinformation",
            "Transparency shifts",
            "Surveillance changes",
            "Leak/disclosure events",
            "Asymmetric knowledge",
            "Delayed information",
            "Data quality issues"
        ],
        example_breaches=[
            "Satellite surveillance degraded for 90 days, blinding decision-makers",
            "Adversary has penetrating intelligence on strategy, counters every move",
            "Whistleblower leak forces complete strategic transparency",
            "Sophisticated deepfake campaign creates false crisis indicators",
            "Real-time sensor data proves systematically biased, decisions flawed"
        ]
    ),

    "external_shocks": StrategicAxis(
        id="external_shocks",
        name="External Shocks/Black Swans",
        description=(
            "Explores how unanticipated external events disrupt scenarios. "
            "Examines natural disasters, technological breakthroughs, pandemics, and wild card events. "
            "Tests assumptions about environmental stability and the boundary of 'possible' events."
        ),
        prompt_template=(
            "Given the fragility: {fragility_description}\n\n"
            "Generate a breach condition involving an external shock:\n"
            "- What if an unanticipated natural disaster occurs?\n"
            "- What if a technological breakthrough changes the game?\n"
            "- What if a pandemic, climate event, or other systemic shock hits?\n"
            "- What if multiple low-probability events coincide?\n\n"
            "Create a specific external shock trigger that is plausible but outside "
            "the baseline scenario's scope, invalidating environmental stability assumptions."
        ),
        focus_areas=[
            "Natural disasters",
            "Pandemics/health crises",
            "Climate events",
            "Technological disruption",
            "Market crashes",
            "Social upheaval",
            "Cyber attacks",
            "Asteroid/cosmic events"
        ],
        example_breaches=[
            "9.0 earthquake destroys critical infrastructure during crisis response",
            "Novel pandemic emerges, forcing 18-month global shutdown",
            "Breakthrough AI capability shifts military balance overnight",
            "Three major economies simultaneously enter currency crisis",
            "Solar storm disables satellites and power grids for 6 months"
        ]
    )
}


def get_axis(axis_id: str) -> StrategicAxis:
    """Get a strategic axis by ID."""
    return STRATEGIC_AXES.get(axis_id)


def get_all_axes() -> List[StrategicAxis]:
    """Get all strategic axes."""
    return list(STRATEGIC_AXES.values())


def get_axes_by_fragility_type(fragility_type: str) -> List[str]:
    """
    Map fragility types to relevant strategic axes.
    Returns list of axis IDs most relevant to the fragility type.
    """
    mapping = {
        "cascade_failure": ["structural_failures", "temporal_shifts"],
        "timing_mismatch": ["temporal_shifts", "resource_constraints"],
        "incentive_misalignment": ["actor_behavior", "structural_failures"],
        "resource_constraint": ["resource_constraints", "external_shocks"],
        "capability_gap": ["actor_behavior", "information_asymmetry"],
        "concentration_risk": ["structural_failures", "resource_constraints"],
        "dependency_failure": ["structural_failures", "temporal_shifts"],
        "information_gap": ["information_asymmetry", "actor_behavior"],
        "assumption_weakness": ["information_asymmetry", "external_shocks"],
    }

    return mapping.get(fragility_type, ["external_shocks"])  # Default fallback


def get_prompt_for_axis(axis_id: str, fragility_description: str, context: Dict = None) -> str:
    """
    Generate a customized prompt for breach condition generation.

    Args:
        axis_id: Strategic axis identifier
        fragility_description: Description of the fragility point
        context: Optional additional context (duration, actors, resources, etc.)

    Returns:
        Formatted prompt string for LLM
    """
    axis = get_axis(axis_id)
    if not axis:
        raise ValueError(f"Unknown axis: {axis_id}")

    prompt = axis.prompt_template.format(
        fragility_description=fragility_description,
        duration=context.get("duration", "6 months") if context else "6 months"
    )

    return prompt


def validate_axis_coverage(counterfactuals: List[Dict]) -> Dict:
    """
    Validate that counterfactuals cover all six axes adequately.

    Args:
        counterfactuals: List of counterfactual dictionaries with 'axis' field

    Returns:
        Coverage report with counts per axis and warnings
    """
    axis_counts = {axis_id: 0 for axis_id in STRATEGIC_AXES.keys()}

    for cf in counterfactuals:
        axis_id = cf.get("axis")
        if axis_id in axis_counts:
            axis_counts[axis_id] += 1

    total = len(counterfactuals)
    warnings = []

    for axis_id, count in axis_counts.items():
        if count == 0:
            warnings.append(f"No counterfactuals for axis: {STRATEGIC_AXES[axis_id].name}")
        elif count < 2:
            warnings.append(f"Only {count} counterfactual for axis: {STRATEGIC_AXES[axis_id].name} (recommend 2-3)")

    return {
        "total_counterfactuals": total,
        "by_axis": {STRATEGIC_AXES[k].name: v for k, v in axis_counts.items()},
        "coverage_complete": len(warnings) == 0,
        "warnings": warnings,
        "target": "18+ counterfactuals (3 per axis × 6 axes)"
    }
