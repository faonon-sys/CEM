"""
Sprint 3 - Task 1: Multi-Dimensional Question Template Library

Comprehensive library of question templates organized across four core dimensions:
- Temporal (timeline dependencies, sequence assumptions)
- Structural (system architecture, component relationships)
- Actor-based (stakeholder motivations, capability assumptions)
- Resource-based (availability, allocation, constraints)
"""

import json
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class QuestionDimension(str, Enum):
    """Four core questioning dimensions."""
    TEMPORAL = "temporal"
    STRUCTURAL = "structural"
    ACTOR_BASED = "actor_based"
    RESOURCE_BASED = "resource_based"


class SeverityFocus(str, Enum):
    """Types of vulnerabilities questions target."""
    CASCADE_FAILURE = "cascade_failure"
    TIMING_MISMATCH = "timing_mismatch"
    INCENTIVE_MISALIGNMENT = "incentive_misalignment"
    RESOURCE_CONSTRAINT = "resource_constraint"
    DEPENDENCY_FAILURE = "dependency_failure"
    CAPABILITY_GAP = "capability_gap"
    SEQUENCE_DISRUPTION = "sequence_disruption"
    CONCENTRATION_RISK = "concentration_risk"


class QuestionTemplate:
    """Represents a single question template with metadata."""

    def __init__(
        self,
        template_id: str,
        dimension: QuestionDimension,
        template_text: str,
        variables: List[str],
        applicability: List[str],
        severity_focus: SeverityFocus,
        assumption_types: List[str],
        explanation: str,
        follow_up: Optional[str] = None
    ):
        self.template_id = template_id
        self.dimension = dimension
        self.template_text = template_text
        self.variables = variables
        self.applicability = applicability
        self.severity_focus = severity_focus
        self.assumption_types = assumption_types
        self.explanation = explanation
        self.follow_up = follow_up

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "template_id": self.template_id,
            "dimension": self.dimension.value,
            "template_text": self.template_text,
            "variables": self.variables,
            "applicability": self.applicability,
            "severity_focus": self.severity_focus.value,
            "assumption_types": self.assumption_types,
            "explanation": self.explanation,
            "follow_up": self.follow_up
        }


class QuestionTemplateLibrary:
    """
    Comprehensive library of 60+ question templates across 4 dimensions.

    Each template includes:
    - Parameterized text with variable placeholders
    - Metadata about applicability conditions
    - Links to assumption categories
    - Severity focus areas
    """

    def __init__(self):
        self.templates: List[QuestionTemplate] = []
        self._load_templates()
        logger.info(f"Loaded {len(self.templates)} question templates across 4 dimensions")

    def _load_templates(self):
        """Load all question templates organized by dimension."""

        # ==================== TEMPORAL DIMENSION ====================
        # 15+ questions about timeline dependencies and sequence assumptions

        temporal_templates = [
            QuestionTemplate(
                template_id="temp_001",
                dimension=QuestionDimension.TEMPORAL,
                template_text="If {event_a} is delayed by {duration}, what prevents {event_b} from proceeding as planned?",
                variables=["event_a", "duration", "event_b"],
                applicability=["project_timeline", "sequential_dependencies", "critical_path"],
                severity_focus=SeverityFocus.SEQUENCE_DISRUPTION,
                assumption_types=["timeline", "dependency"],
                explanation="Tests whether downstream events have genuine independence or hidden dependencies on predecessor timing."
            ),
            QuestionTemplate(
                template_id="temp_002",
                dimension=QuestionDimension.TEMPORAL,
                template_text="What happens if {actor} needs {duration_longer} longer than expected to complete {task}?",
                variables=["actor", "duration_longer", "task"],
                applicability=["capacity_planning", "resource_scheduling", "execution_timeline"],
                severity_focus=SeverityFocus.TIMING_MISMATCH,
                assumption_types=["capacity", "timeline", "performance"],
                explanation="Examines buffer assumptions and cascade effects of timeline slippage."
            ),
            QuestionTemplate(
                template_id="temp_003",
                dimension=QuestionDimension.TEMPORAL,
                template_text="By what date must {critical_decision} be made to keep {outcome} achievable?",
                variables=["critical_decision", "outcome"],
                applicability=["decision_timing", "strategic_planning", "point_of_no_return"],
                severity_focus=SeverityFocus.TIMING_MISMATCH,
                assumption_types=["decision_timing", "reversibility"],
                explanation="Identifies hidden decision deadlines and irreversible commitment points.",
                follow_up="What forces could compress or extend this decision window?"
            ),
            QuestionTemplate(
                template_id="temp_004",
                dimension=QuestionDimension.TEMPORAL,
                template_text="If we had to accelerate {timeline} by {percentage}%, what would break first?",
                variables=["timeline", "percentage"],
                applicability=["schedule_compression", "crisis_response", "rapid_deployment"],
                severity_focus=SeverityFocus.SEQUENCE_DISRUPTION,
                assumption_types=["feasibility", "constraints", "dependencies"],
                explanation="Stress-tests timeline assumptions to reveal critical path bottlenecks."
            ),
            QuestionTemplate(
                template_id="temp_005",
                dimension=QuestionDimension.TEMPORAL,
                template_text="What must remain true for the next {time_period} for {assumption} to hold?",
                variables=["time_period", "assumption"],
                applicability=["assumption_duration", "stability_requirements", "environmental_conditions"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["environmental", "stability", "continuity"],
                explanation="Tests temporal boundaries of assumption validity."
            ),
            QuestionTemplate(
                template_id="temp_006",
                dimension=QuestionDimension.TEMPORAL,
                template_text="How long can {system} operate if {input} stops flowing at time {T}?",
                variables=["system", "input", "T"],
                applicability=["supply_continuity", "inventory_management", "resilience"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["buffer_capacity", "inventory", "continuity"],
                explanation="Reveals buffer capacity and hidden inventory assumptions."
            ),
            QuestionTemplate(
                template_id="temp_007",
                dimension=QuestionDimension.TEMPORAL,
                template_text="What early warning signals indicate {assumption} is starting to fail?",
                variables=["assumption"],
                applicability=["monitoring", "risk_detection", "early_warning"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["monitoring", "detection", "response_time"],
                explanation="Tests whether monitoring systems exist to detect assumption breach."
            ),
            QuestionTemplate(
                template_id="temp_008",
                dimension=QuestionDimension.TEMPORAL,
                template_text="If {event_a} and {event_b} occur simultaneously instead of sequentially, what conflicts arise?",
                variables=["event_a", "event_b"],
                applicability=["concurrency", "resource_conflicts", "coordination"],
                severity_focus=SeverityFocus.SEQUENCE_DISRUPTION,
                assumption_types=["sequencing", "resource_allocation", "coordination"],
                explanation="Examines assumptions about event ordering and resource availability."
            ),
            QuestionTemplate(
                template_id="temp_009",
                dimension=QuestionDimension.TEMPORAL,
                template_text="How much advance notice is needed before {change} to avoid disrupting {process}?",
                variables=["change", "process"],
                applicability=["change_management", "adaptation_time", "transition_planning"],
                severity_focus=SeverityFocus.TIMING_MISMATCH,
                assumption_types=["adaptation_capacity", "lead_time", "flexibility"],
                explanation="Reveals assumptions about organizational/system adaptation speed."
            ),
            QuestionTemplate(
                template_id="temp_010",
                dimension=QuestionDimension.TEMPORAL,
                template_text="What is the minimum viable timeline for {outcome}, and what would we sacrifice to achieve it?",
                variables=["outcome"],
                applicability=["timeline_optimization", "tradeoff_analysis", "minimum_viable"],
                severity_focus=SeverityFocus.SEQUENCE_DISRUPTION,
                assumption_types=["tradeoffs", "optimization", "constraints"],
                explanation="Forces explicit acknowledgment of timeline-quality tradeoffs."
            ),
            QuestionTemplate(
                template_id="temp_011",
                dimension=QuestionDimension.TEMPORAL,
                template_text="If {cyclical_event} occurs {frequency_change} more/less frequently, how does that cascade through {system}?",
                variables=["cyclical_event", "frequency_change", "system"],
                applicability=["cyclical_processes", "frequency_assumptions", "rhythm_changes"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["cyclical", "frequency", "synchronization"],
                explanation="Tests assumptions about operational rhythms and synchronization."
            ),
            QuestionTemplate(
                template_id="temp_012",
                dimension=QuestionDimension.TEMPORAL,
                template_text="At what point does delay in {component} transition from manageable to catastrophic?",
                variables=["component"],
                applicability=["threshold_identification", "tipping_points", "critical_delays"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["thresholds", "tipping_points", "nonlinear_effects"],
                explanation="Identifies nonlinear effects and tipping points in temporal dependencies."
            ),
            QuestionTemplate(
                template_id="temp_013",
                dimension=QuestionDimension.TEMPORAL,
                template_text="How quickly can {system} detect and respond to {failure_condition}?",
                variables=["system", "failure_condition"],
                applicability=["response_time", "detection_capabilities", "recovery"],
                severity_focus=SeverityFocus.TIMING_MISMATCH,
                assumption_types=["detection_speed", "response_capacity", "recovery_time"],
                explanation="Tests assumptions about detection speed and response capabilities."
            ),
            QuestionTemplate(
                template_id="temp_014",
                dimension=QuestionDimension.TEMPORAL,
                template_text="What seasonal, cyclical, or periodic factors could change the timeline for {outcome}?",
                variables=["outcome"],
                applicability=["seasonal_factors", "cyclical_influences", "periodic_effects"],
                severity_focus=SeverityFocus.TIMING_MISMATCH,
                assumption_types=["seasonality", "cyclical", "environmental"],
                explanation="Reveals hidden temporal dependencies on cyclical patterns."
            ),
            QuestionTemplate(
                template_id="temp_015",
                dimension=QuestionDimension.TEMPORAL,
                template_text="If {event} happens {duration} earlier than planned, are prerequisites in place?",
                variables=["event", "duration"],
                applicability=["early_acceleration", "prerequisite_readiness", "opportunistic_timing"],
                severity_focus=SeverityFocus.SEQUENCE_DISRUPTION,
                assumption_types=["prerequisites", "readiness", "opportunistic"],
                explanation="Tests assumptions about prerequisite sequencing and readiness."
            ),
        ]

        # ==================== STRUCTURAL DIMENSION ====================
        # 15+ questions about system architecture and component relationships

        structural_templates = [
            QuestionTemplate(
                template_id="struct_001",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="If {component} fails completely, what prevents {dependent_component} from continuing operation?",
                variables=["component", "dependent_component"],
                applicability=["system_architecture", "dependencies", "single_point_of_failure"],
                severity_focus=SeverityFocus.DEPENDENCY_FAILURE,
                assumption_types=["redundancy", "availability", "fault_tolerance"],
                explanation="Exposes single points of failure and tests redundancy assumptions."
            ),
            QuestionTemplate(
                template_id="struct_002",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="How many critical components must fail simultaneously before {system} ceases to function?",
                variables=["system"],
                applicability=["resilience", "fault_tolerance", "redundancy"],
                severity_focus=SeverityFocus.CONCENTRATION_RISK,
                assumption_types=["redundancy", "resilience", "critical_mass"],
                explanation="Reveals assumptions about system resilience and failure thresholds."
            ),
            QuestionTemplate(
                template_id="struct_003",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="What alternative pathways exist if the connection between {component_a} and {component_b} breaks?",
                variables=["component_a", "component_b"],
                applicability=["network_topology", "routing", "alternative_paths"],
                severity_focus=SeverityFocus.DEPENDENCY_FAILURE,
                assumption_types=["connectivity", "routing", "alternatives"],
                explanation="Tests assumptions about network topology and alternative pathways."
            ),
            QuestionTemplate(
                template_id="struct_004",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="If we remove {component} entirely, what workarounds or manual processes could substitute?",
                variables=["component"],
                applicability=["criticality_assessment", "substitutability", "workarounds"],
                severity_focus=SeverityFocus.DEPENDENCY_FAILURE,
                assumption_types=["substitutability", "manual_fallback", "essentiality"],
                explanation="Reveals whether components are truly essential or just convenient."
            ),
            QuestionTemplate(
                template_id="struct_005",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="What hidden dependencies does {component} have on {infrastructure} that aren't documented?",
                variables=["component", "infrastructure"],
                applicability=["hidden_dependencies", "documentation_gaps", "infrastructure"],
                severity_focus=SeverityFocus.DEPENDENCY_FAILURE,
                assumption_types=["dependencies", "infrastructure", "documentation"],
                explanation="Uncovers undocumented or implicit infrastructure dependencies."
            ),
            QuestionTemplate(
                template_id="struct_006",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="If demand on {component} increases by {percentage}%, where does the system break?",
                variables=["component", "percentage"],
                applicability=["scalability", "capacity_limits", "stress_testing"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["scalability", "capacity", "bottlenecks"],
                explanation="Stress-tests capacity assumptions and reveals bottlenecks."
            ),
            QuestionTemplate(
                template_id="struct_007",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="How does degraded performance in {component} cascade to {downstream_system}?",
                variables=["component", "downstream_system"],
                applicability=["cascade_effects", "performance_degradation", "interdependencies"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["cascading", "performance", "interdependencies"],
                explanation="Maps cascade effects of performance degradation through system."
            ),
            QuestionTemplate(
                template_id="struct_008",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="What percentage of {system} functionality depends on {single_vendor} or {single_provider}?",
                variables=["system", "single_vendor", "single_provider"],
                applicability=["vendor_concentration", "supplier_risk", "monopoly_dependencies"],
                severity_focus=SeverityFocus.CONCENTRATION_RISK,
                assumption_types=["concentration", "vendor_lock", "diversification"],
                explanation="Reveals concentration risks and vendor lock-in assumptions."
            ),
            QuestionTemplate(
                template_id="struct_009",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="If {component} must operate in degraded mode, what capabilities are lost and what remains?",
                variables=["component"],
                applicability=["graceful_degradation", "fallback_modes", "core_functionality"],
                severity_focus=SeverityFocus.DEPENDENCY_FAILURE,
                assumption_types=["degraded_mode", "core_vs_auxiliary", "graceful_degradation"],
                explanation="Tests assumptions about graceful degradation and core functionality."
            ),
            QuestionTemplate(
                template_id="struct_010",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="What interface or protocol changes would break compatibility between {system_a} and {system_b}?",
                variables=["system_a", "system_b"],
                applicability=["integration", "compatibility", "interface_stability"],
                severity_focus=SeverityFocus.DEPENDENCY_FAILURE,
                assumption_types=["compatibility", "interface_stability", "versioning"],
                explanation="Reveals fragile integration assumptions and version dependencies."
            ),
            QuestionTemplate(
                template_id="struct_011",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="How centralized vs. distributed is control of {system}, and what does that imply for failure modes?",
                variables=["system"],
                applicability=["architecture_topology", "centralization", "control_structure"],
                severity_focus=SeverityFocus.CONCENTRATION_RISK,
                assumption_types=["centralization", "topology", "control_structure"],
                explanation="Examines architectural centralization and its vulnerability implications."
            ),
            QuestionTemplate(
                template_id="struct_012",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="If physical access to {location} is lost, what remote capabilities remain functional?",
                variables=["location"],
                applicability=["physical_dependencies", "remote_capabilities", "location_risk"],
                severity_focus=SeverityFocus.DEPENDENCY_FAILURE,
                assumption_types=["physical_access", "remote_operation", "location"],
                explanation="Tests assumptions about physical dependencies vs. remote capabilities."
            ),
            QuestionTemplate(
                template_id="struct_013",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="What common infrastructure do {system_a} and {system_b} share, creating correlated failure risk?",
                variables=["system_a", "system_b"],
                applicability=["correlated_failures", "shared_infrastructure", "common_mode"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["correlation", "shared_infrastructure", "common_mode_failure"],
                explanation="Identifies common-mode failure risks from shared infrastructure."
            ),
            QuestionTemplate(
                template_id="struct_014",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="How tightly coupled are the components of {system}, and what does that mean for change propagation?",
                variables=["system"],
                applicability=["coupling", "modularity", "change_propagation"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["coupling", "modularity", "change_impact"],
                explanation="Assesses system coupling and implications for change management."
            ),
            QuestionTemplate(
                template_id="struct_015",
                dimension=QuestionDimension.STRUCTURAL,
                template_text="What quality or performance degradation in {component} would be undetectable until catastrophic failure?",
                variables=["component"],
                applicability=["monitoring_gaps", "hidden_degradation", "silent_failure"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["monitoring", "visibility", "early_warning"],
                explanation="Reveals monitoring blind spots and silent failure modes."
            ),
        ]

        # ==================== ACTOR-BASED DIMENSION ====================
        # 15+ questions about stakeholder motivations and capabilities

        actor_templates = [
            QuestionTemplate(
                template_id="actor_001",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="What would {actor} need to believe or prioritize differently to behave contrary to {assumed_behavior}?",
                variables=["actor", "assumed_behavior"],
                applicability=["motivation", "incentives", "behavioral_assumptions"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["motivation", "priorities", "beliefs"],
                explanation="Tests assumptions about actor motivations and decision criteria."
            ),
            QuestionTemplate(
                template_id="actor_002",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="Does {actor} have the capability to {action}, or are we assuming competencies they may lack?",
                variables=["actor", "action"],
                applicability=["capability_assessment", "competency", "capacity"],
                severity_focus=SeverityFocus.CAPABILITY_GAP,
                assumption_types=["capability", "competency", "capacity"],
                explanation="Reveals assumptions about actor capabilities vs. actual competencies."
            ),
            QuestionTemplate(
                template_id="actor_003",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="If {actor_a} and {actor_b} have conflicting interests regarding {issue}, who prevails and why?",
                variables=["actor_a", "actor_b", "issue"],
                applicability=["conflict_resolution", "power_dynamics", "competing_interests"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["power_balance", "conflict_resolution", "interests"],
                explanation="Exposes hidden assumptions about power dynamics and conflict resolution."
            ),
            QuestionTemplate(
                template_id="actor_004",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="What incentives might lead {actor} to defect from {cooperation_arrangement}?",
                variables=["actor", "cooperation_arrangement"],
                applicability=["cooperation", "incentive_alignment", "defection_risk"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["incentives", "cooperation", "defection"],
                explanation="Tests stability of cooperation assumptions via incentive analysis."
            ),
            QuestionTemplate(
                template_id="actor_005",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="How would {actor}'s behavior change if they knew {information} that we assume they don't?",
                variables=["actor", "information"],
                applicability=["information_asymmetry", "strategic_behavior", "game_theory"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["information", "strategic_behavior", "transparency"],
                explanation="Examines assumptions about information asymmetries and strategic behavior."
            ),
            QuestionTemplate(
                template_id="actor_006",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="If leadership of {organization} changes, how stable is their commitment to {policy}?",
                variables=["organization", "policy"],
                applicability=["policy_continuity", "leadership_transition", "institutional_memory"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["continuity", "leadership", "institutional"],
                explanation="Tests assumptions about policy continuity across leadership transitions."
            ),
            QuestionTemplate(
                template_id="actor_007",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="What would {actor} sacrifice to achieve {goal}, and is that sacrifice realistic?",
                variables=["actor", "goal"],
                applicability=["commitment", "tradeoffs", "prioritization"],
                severity_focus=SeverityFocus.CAPABILITY_GAP,
                assumption_types=["commitment", "tradeoffs", "priorities"],
                explanation="Reveals assumptions about actor commitment levels and willingness to sacrifice."
            ),
            QuestionTemplate(
                template_id="actor_008",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="Does {actor} have veto power over {decision}, and if so, what would trigger them to use it?",
                variables=["actor", "decision"],
                applicability=["decision_authority", "veto_power", "governance"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["authority", "veto", "governance"],
                explanation="Identifies hidden veto points and assumptions about decision authority."
            ),
            QuestionTemplate(
                template_id="actor_009",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="How aligned are the incentives of {front_line_actors} with the intentions of {leadership}?",
                variables=["front_line_actors", "leadership"],
                applicability=["principal_agent", "implementation", "incentive_alignment"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["principal_agent", "alignment", "implementation"],
                explanation="Tests principal-agent assumptions and implementation fidelity."
            ),
            QuestionTemplate(
                template_id="actor_010",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="If {external_actor} wanted to disrupt {plan}, what leverage points would they exploit?",
                variables=["external_actor", "plan"],
                applicability=["adversarial_analysis", "red_teaming", "vulnerability"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["adversarial", "vulnerability", "disruption"],
                explanation="Red-teams scenario from adversarial perspective to find vulnerabilities."
            ),
            QuestionTemplate(
                template_id="actor_011",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="What resources must {actor} control to execute {action}, and do they actually control them?",
                variables=["actor", "action"],
                applicability=["resource_control", "authority", "actual_power"],
                severity_focus=SeverityFocus.CAPABILITY_GAP,
                assumption_types=["resource_control", "authority", "power"],
                explanation="Distinguishes formal authority from actual resource control."
            ),
            QuestionTemplate(
                template_id="actor_012",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="How might {actor}'s internal politics or factions prevent unified action on {issue}?",
                variables=["actor", "issue"],
                applicability=["internal_cohesion", "factions", "collective_action"],
                severity_focus=SeverityFocus.CAPABILITY_GAP,
                assumption_types=["cohesion", "internal_politics", "unity"],
                explanation="Examines assumptions about internal organizational cohesion."
            ),
            QuestionTemplate(
                template_id="actor_013",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="What past behavior of {actor} contradicts the assumption that they will {future_behavior}?",
                variables=["actor", "future_behavior"],
                applicability=["historical_consistency", "behavior_prediction", "track_record"],
                severity_focus=SeverityFocus.CAPABILITY_GAP,
                assumption_types=["historical", "consistency", "prediction"],
                explanation="Tests behavioral assumptions against historical track record."
            ),
            QuestionTemplate(
                template_id="actor_014",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="If {actor} faces a choice between {short_term_incentive} and {long_term_goal}, which will they choose?",
                variables=["actor", "short_term_incentive", "long_term_goal"],
                applicability=["time_preference", "discount_rates", "temporal_tradeoffs"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["time_preference", "tradeoffs", "incentives"],
                explanation="Reveals assumptions about actor time preferences and discount rates."
            ),
            QuestionTemplate(
                template_id="actor_015",
                dimension=QuestionDimension.ACTOR_BASED,
                template_text="What audience is {actor} signaling to with {action}, and how does that constrain their options?",
                variables=["actor", "action"],
                applicability=["signaling", "reputation", "audience_constraints"],
                severity_focus=SeverityFocus.INCENTIVE_MISALIGNMENT,
                assumption_types=["signaling", "reputation", "constraints"],
                explanation="Examines how signaling and reputation concerns constrain behavior."
            ),
        ]

        # ==================== RESOURCE-BASED DIMENSION ====================
        # 15+ questions about availability, allocation, and constraints

        resource_templates = [
            QuestionTemplate(
                template_id="resource_001",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="If availability of {resource} drops by {percentage}%, which activities must be curtailed first?",
                variables=["resource", "percentage"],
                applicability=["resource_scarcity", "prioritization", "rationing"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["availability", "allocation", "prioritization"],
                explanation="Forces explicit prioritization when resources become scarce."
            ),
            QuestionTemplate(
                template_id="resource_002",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="What is the lead time to acquire additional {resource}, and can that resource be acquired at any scale?",
                variables=["resource"],
                applicability=["supply_elasticity", "lead_times", "scalability"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["elasticity", "lead_time", "scalability"],
                explanation="Tests assumptions about resource supply elasticity and acquisition speed."
            ),
            QuestionTemplate(
                template_id="resource_003",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="How many alternative suppliers or sources exist for {resource}, and how quickly can we switch?",
                variables=["resource"],
                applicability=["supplier_diversity", "substitution", "switching_costs"],
                severity_focus=SeverityFocus.CONCENTRATION_RISK,
                assumption_types=["diversification", "substitution", "switching"],
                explanation="Reveals supplier concentration risks and switching cost assumptions."
            ),
            QuestionTemplate(
                template_id="resource_004",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="If cost of {resource} increases by {percentage}%, what becomes economically unviable?",
                variables=["resource", "percentage"],
                applicability=["cost_sensitivity", "economic_viability", "margins"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["cost_sensitivity", "margins", "viability"],
                explanation="Stress-tests economic viability assumptions under cost pressure."
            ),
            QuestionTemplate(
                template_id="resource_005",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="What inventory or buffer of {resource} exists, and how long can operations continue without resupply?",
                variables=["resource"],
                applicability=["buffer_capacity", "inventory", "continuity"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["inventory", "buffer", "continuity"],
                explanation="Quantifies buffer assumptions and supply interruption tolerance."
            ),
            QuestionTemplate(
                template_id="resource_006",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="If demand for {resource} spikes unexpectedly, who else competes for the same resource pool?",
                variables=["resource"],
                applicability=["competition", "demand_shocks", "allocation_conflicts"],
                severity_focus=SeverityFocus.CONCENTRATION_RISK,
                assumption_types=["competition", "demand", "allocation"],
                explanation="Identifies hidden competition for shared resource pools."
            ),
            QuestionTemplate(
                template_id="resource_007",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="What percentage of {budget} is committed vs. discretionary, and how flexible is reallocation?",
                variables=["budget"],
                applicability=["budget_flexibility", "financial_constraints", "reallocation"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["budget", "flexibility", "committed_costs"],
                explanation="Tests assumptions about budget flexibility and reallocation capacity."
            ),
            QuestionTemplate(
                template_id="resource_008",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="If {resource_a} and {resource_b} cannot both be acquired simultaneously, which takes priority?",
                variables=["resource_a", "resource_b"],
                applicability=["tradeoffs", "prioritization", "mutual_exclusivity"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["tradeoffs", "prioritization", "exclusivity"],
                explanation="Forces explicit tradeoff decisions between competing resource needs."
            ),
            QuestionTemplate(
                template_id="resource_009",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="What geopolitical, regulatory, or market conditions could suddenly restrict access to {resource}?",
                variables=["resource"],
                applicability=["access_risk", "geopolitical", "regulatory"],
                severity_focus=SeverityFocus.CONCENTRATION_RISK,
                assumption_types=["access", "geopolitical", "regulatory"],
                explanation="Examines external factors that could disrupt resource access."
            ),
            QuestionTemplate(
                template_id="resource_010",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="How substitutable is {resource}, and what performance tradeoffs come with substitutes?",
                variables=["resource"],
                applicability=["substitution", "alternatives", "performance_tradeoffs"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["substitutability", "alternatives", "tradeoffs"],
                explanation="Tests assumptions about resource substitutability and quality tradeoffs."
            ),
            QuestionTemplate(
                template_id="resource_011",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="What happens if skilled personnel with knowledge of {capability} become unavailable?",
                variables=["capability"],
                applicability=["key_person_risk", "knowledge_retention", "succession"],
                severity_focus=SeverityFocus.CONCENTRATION_RISK,
                assumption_types=["key_person", "knowledge", "succession"],
                explanation="Reveals key person risks and knowledge concentration assumptions."
            ),
            QuestionTemplate(
                template_id="resource_012",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="If we must operate with {percentage}% less {resource} permanently, what structural changes are needed?",
                variables=["percentage", "resource"],
                applicability=["permanent_scarcity", "structural_adaptation", "efficiency"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["adaptation", "efficiency", "structural_change"],
                explanation="Forces thinking about structural adaptation to permanent scarcity."
            ),
            QuestionTemplate(
                template_id="resource_013",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="What shared infrastructure or common resources create hidden dependencies between {user_a} and {user_b}?",
                variables=["user_a", "user_b"],
                applicability=["shared_resources", "hidden_dependencies", "correlation"],
                severity_focus=SeverityFocus.CASCADE_FAILURE,
                assumption_types=["shared_resources", "dependencies", "correlation"],
                explanation="Identifies correlated risks from shared resource dependencies."
            ),
            QuestionTemplate(
                template_id="resource_014",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="How much overcapacity exists in {resource}, and at what utilization does quality degrade?",
                variables=["resource"],
                applicability=["capacity_margin", "quality_degradation", "utilization"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["capacity", "margin", "quality"],
                explanation="Quantifies capacity margins and quality degradation thresholds."
            ),
            QuestionTemplate(
                template_id="resource_015",
                dimension=QuestionDimension.RESOURCE_BASED,
                template_text="What seasonal or cyclical patterns affect availability of {resource}, and how do we buffer against them?",
                variables=["resource"],
                applicability=["seasonality", "cyclical_supply", "buffering"],
                severity_focus=SeverityFocus.RESOURCE_CONSTRAINT,
                assumption_types=["seasonality", "cyclical", "buffering"],
                explanation="Examines cyclical resource availability and buffering strategies."
            ),
        ]

        # Combine all templates
        self.templates.extend(temporal_templates)
        self.templates.extend(structural_templates)
        self.templates.extend(actor_templates)
        self.templates.extend(resource_templates)

    def get_all_templates(self) -> List[Dict]:
        """Get all templates as dictionaries."""
        return [t.to_dict() for t in self.templates]

    def get_by_dimension(self, dimension: QuestionDimension) -> List[Dict]:
        """Get templates for a specific dimension."""
        return [t.to_dict() for t in self.templates if t.dimension == dimension]

    def get_by_applicability(self, applicability_tag: str) -> List[Dict]:
        """Find templates applicable to a specific context."""
        return [
            t.to_dict() for t in self.templates
            if applicability_tag in t.applicability
        ]

    def get_by_severity_focus(self, severity: SeverityFocus) -> List[Dict]:
        """Get templates targeting a specific vulnerability type."""
        return [t.to_dict() for t in self.templates if t.severity_focus == severity]

    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """Retrieve a specific template by ID."""
        for template in self.templates:
            if template.template_id == template_id:
                return template.to_dict()
        return None

    def search_templates(self, query: str) -> List[Dict]:
        """Search templates by keyword in text or explanation."""
        query_lower = query.lower()
        results = []
        for template in self.templates:
            if (query_lower in template.template_text.lower() or
                query_lower in template.explanation.lower() or
                any(query_lower in var.lower() for var in template.variables)):
                results.append(template.to_dict())
        return results

    def get_statistics(self) -> Dict:
        """Get library statistics."""
        by_dimension = {}
        for dim in QuestionDimension:
            by_dimension[dim.value] = len(self.get_by_dimension(dim))

        by_severity = {}
        for sev in SeverityFocus:
            by_severity[sev.value] = len(self.get_by_severity_focus(sev))

        return {
            "total_templates": len(self.templates),
            "by_dimension": by_dimension,
            "by_severity_focus": by_severity,
            "total_variables": sum(len(t.variables) for t in self.templates),
            "templates_with_followups": sum(1 for t in self.templates if t.follow_up)
        }


# Global instance
template_library = QuestionTemplateLibrary()
