"""
Prompt templates for multi-phase structured reasoning.
"""

# System prompts
REASONING_SYSTEM_PROMPT = """You are an expert analytical system specialized in structured reasoning and strategic analysis. Your role is to systematically deconstruct complex scenarios, challenge assumptions, and explore alternative outcomes through rigorous interrogation."""

# Phase 1: Surface Premise Analysis
ASSUMPTION_EXTRACTION_PROMPT = """Analyze the following scenario and extract the key assumptions underlying it. Identify both explicit and implicit assumptions that form the foundation of the scenario's baseline narrative.

Scenario:
{scenario}

For each assumption, provide:
1. A clear statement of the assumption
2. A category (political, economic, technological, social, operational, strategic, etc.)
3. A confidence level (0.0 to 1.0) indicating how strongly this assumption appears to underpin the scenario

Return your analysis as a JSON object with this structure:
{{
    "assumptions": [
        {{
            "id": "assumption_1",
            "text": "Clear statement of the assumption",
            "category": "category name",
            "confidence": 0.85
        }}
    ]
}}

Focus on identifying 5-15 key assumptions that are load-bearing for the scenario's logic."""

BASELINE_NARRATIVE_PROMPT = """Given the following scenario and extracted assumptions, generate a concise baseline narrative that summarizes the dominant conventional wisdom and expected trajectory.

Scenario:
{scenario}

Assumptions:
{assumptions}

The baseline narrative should be 2-3 paragraphs and should reflect the surface-level understanding that most observers would share about how this scenario will likely unfold."""

# Phase 2: Deep Questioning
PROBING_QUESTIONS_PROMPT = """You are generating interrogative questions to expose hidden fragilities and blind spots in the following assumptions extracted from a complex scenario.

Assumptions:
{assumptions}

For each assumption, generate 2-4 probing questions across these dimensions:

1. **Temporal**: What if the timeline compresses or extends? What if the sequence of events changes?
2. **Structural**: What load-bearing dependencies exist? What if key structural relationships break?
3. **Actor-based**: Whose incentives could shift? What if key actors behave differently than expected?
4. **Resource-based**: What constraints could bind? What if resource availability changes?
5. **Information**: What unknowns could surface? What if hidden information becomes public or vice versa?

Each question should:
- Challenge a specific aspect of an assumption
- Expose a potential vulnerability or blind spot
- Be concrete and scenario-specific (not generic)
- Help identify non-obvious risk vectors

Return your analysis as a JSON object:
{{
    "questions": [
        {{
            "assumption_id": "assumption_1",
            "question_text": "What if X happens instead of Y?",
            "dimension": "temporal"
        }}
    ]
}}"""

# Phase 3: Counterfactual Generation
COUNTERFACTUAL_GENERATION_PROMPT = """Generate counterfactual scenarios by forcing breach conditions on the assumptions and exploring alternative outcomes.

Original Scenario:
{scenario}

Assumptions:
{assumptions}

Vulnerabilities Identified:
{vulnerabilities}

Generate 3-5 counterfactual scenarios across each of these SIX STRATEGIC AXES:

1. **Geopolitical Alignment Shifts**: Changes in alliances, partnerships, or geopolitical positions
2. **Economic Constraint Breaches**: Economic assumptions that fail (funding, markets, resources)
3. **Technological Disruption**: Unexpected technological changes or failures
4. **Actor Strategy Changes**: Key players changing their strategies or goals
5. **Information Environment Shifts**: Changes in what is known, believed, or communicated
6. **Resource Availability Changes**: Critical resources becoming more/less available

For each counterfactual, specify:
- The axis it belongs to
- The specific breach condition (what assumption fails and how)
- Cascading consequences (what happens as a result)
- Severity rating (1-10)
- Probability estimate (0.0-1.0)

Return as JSON:
{{
    "counterfactuals": [
        {{
            "axis": "geopolitical_alignment",
            "breach_condition": "Specific description of what fails",
            "consequences": [
                {{"description": "First-order effect", "severity": 7, "timeframe": "immediate"}},
                {{"description": "Second-order effect", "severity": 8, "timeframe": "3-6 months"}}
            ],
            "severity_rating": 8,
            "probability_rating": 0.25
        }}
    ]
}}"""

# Phase 5: Strategic Outcomes
STRATEGIC_OUTCOME_PROMPT = """Project the strategic outcome trajectory for the following counterfactual scenario.

Breach Condition:
{breach_condition}

Consequences:
{consequences}

Strategic Axis:
{axis}

Generate a trajectory projection that includes:

1. **Timeline Milestones**: Key events at T+1month, T+3months, T+6months, T+1year
2. **Decision Points**: Critical moments where interventions could alter the trajectory
3. **Inflection Points**: Moments where the trajectory could branch significantly
4. **Confidence Intervals**: How certainty decreases over the time horizon

Return as JSON:
{{
    "trajectory": {{
        "T+1month": {{"events": ["event1", "event2"], "status": "description"}},
        "T+3months": {{"events": ["event1", "event2"], "status": "description"}},
        "T+6months": {{"events": ["event1", "event2"], "status": "description"}},
        "T+1year": {{"events": ["event1", "event2"], "status": "description"}}
    }},
    "decision_points": [
        {{
            "time": "T+2months",
            "description": "Critical decision required",
            "options": ["option1", "option2"],
            "criticality": 8
        }}
    ],
    "inflection_points": [
        {{
            "time": "T+4months",
            "description": "Trajectory branch point",
            "branches": ["path1", "path2"]
        }}
    ],
    "confidence_intervals": {{
        "T+1month": 0.85,
        "T+3months": 0.65,
        "T+6months": 0.45,
        "T+1year": 0.25
    }}
}}"""


class PromptLibrary:
    """Library of prompt templates for structured reasoning."""

    def __init__(self):
        self.templates = {
            "assumption_extraction": ASSUMPTION_EXTRACTION_PROMPT,
            "baseline_narrative": BASELINE_NARRATIVE_PROMPT,
            "probing_questions": PROBING_QUESTIONS_PROMPT,
            "counterfactual_generation": COUNTERFACTUAL_GENERATION_PROMPT,
            "strategic_outcome": STRATEGIC_OUTCOME_PROMPT
        }

    def get(self, template_name: str) -> str:
        """Get a prompt template by name."""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        return self.templates[template_name]

    def format(self, template_name: str, **kwargs) -> str:
        """Get and format a prompt template with variables."""
        template = self.get(template_name)
        return template.format(**kwargs)
