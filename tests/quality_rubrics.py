"""
Quality Evaluation Rubrics for Output Validation
Systematic scoring of assumptions, questions, and counterfactuals
"""
from typing import List, Dict, Any
import re


class QualityRubric:
    """Automated quality scoring for reasoning outputs"""

    @staticmethod
    def evaluate_assumptions(assumptions: List[Dict[str, Any]]) -> float:
        """
        Score assumption quality on 0-10 scale
        Metrics: specificity, verifiability, completeness, accuracy
        """
        if not assumptions:
            return 0.0

        scores = {
            'specificity': 0.0,
            'verifiability': 0.0,
            'completeness': 0.0,
            'accuracy': 0.0
        }

        # 1. Specificity: Avoid vague language
        vague_words = ['might', 'could', 'possibly', 'generally', 'usually',
                       'maybe', 'perhaps', 'sometimes', 'often']
        specific_count = 0
        for assumption in assumptions:
            description = assumption.get("description", "").lower()
            if not any(word in description for word in vague_words):
                specific_count += 1
        scores['specificity'] = (specific_count / len(assumptions)) * 10

        # 2. Verifiability: Can be fact-checked
        # Look for quantifiable/measurable statements
        verifiable_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+\s*(year|month|day|week)',  # Time periods
            r'(increase|decrease|grow|shrink|rise|fall)',  # Change verbs
        ]
        verifiable_count = 0
        for assumption in assumptions:
            description = assumption.get("description", "").lower()
            if any(re.search(pattern, description) for pattern in verifiable_patterns):
                verifiable_count += 1
        scores['verifiability'] = (verifiable_count / len(assumptions)) * 10

        # 3. Completeness: Cover multiple domains
        domains = set(a.get("domain", "") for a in assumptions)
        expected_domains = {'political', 'economic', 'operational', 'social',
                           'technical', 'environmental'}
        domain_coverage = len(domains & expected_domains) / len(expected_domains)
        scores['completeness'] = domain_coverage * 10

        # 4. Accuracy: Well-formed with required fields
        accurate_count = sum(
            1 for a in assumptions
            if all(key in a for key in ['description', 'domain', 'confidence'])
            and len(a.get('description', '')) > 20  # Substantive description
        )
        scores['accuracy'] = (accurate_count / len(assumptions)) * 10

        overall_score = sum(scores.values()) / len(scores)
        return round(overall_score, 2)

    @staticmethod
    def evaluate_questions(questions: List[Dict[str, Any]]) -> float:
        """
        Score question quality on 0-10 scale
        Metrics: depth, coverage, relevance, actionability
        """
        if not questions:
            return 0.0

        scores = {
            'depth': 0.0,
            'coverage': 0.0,
            'relevance': 0.0,
            'actionability': 0.0
        }

        # 1. Depth: Deep probing vs surface questions
        deep_indicators = ['why', 'how', 'what if', 'under what conditions',
                          'what would happen', 'what prevents', 'what enables']
        deep_count = 0
        for question in questions:
            text = question.get("text", "").lower()
            if any(indicator in text for indicator in deep_indicators):
                deep_count += 1
        scores['depth'] = (deep_count / len(questions)) * 10

        # 2. Coverage: Multiple questioning dimensions
        dimensions = set(q.get("dimension", "") for q in questions)
        expected_dimensions = {'temporal', 'structural', 'actor', 'resource',
                              'information'}
        dimension_coverage = len(dimensions & expected_dimensions) / len(expected_dimensions)
        scores['coverage'] = dimension_coverage * 10

        # 3. Relevance: Questions challenge assumptions
        # Look for assumption linkage
        linked_count = sum(
            1 for q in questions
            if 'assumption_id' in q or 'related_assumption' in q
        )
        scores['relevance'] = (linked_count / len(questions)) * 10

        # 4. Actionability: Questions that lead to insights
        # Look for consequence-focused questions
        actionable_patterns = [
            'impact', 'effect', 'consequence', 'result', 'outcome',
            'change', 'alter', 'affect', 'influence'
        ]
        actionable_count = 0
        for question in questions:
            text = question.get("text", "").lower()
            if any(pattern in text for pattern in actionable_patterns):
                actionable_count += 1
        scores['actionability'] = (actionable_count / len(questions)) * 10

        overall_score = sum(scores.values()) / len(scores)
        return round(overall_score, 2)

    @staticmethod
    def evaluate_counterfactuals(counterfactuals: List[Dict[str, Any]]) -> float:
        """
        Score counterfactual quality on 0-10 scale
        Metrics: plausibility, specificity, consequences, diversity
        """
        if not counterfactuals:
            return 0.0

        scores = {
            'plausibility': 0.0,
            'specificity': 0.0,
            'consequences': 0.0,
            'diversity': 0.0
        }

        # 1. Plausibility: Realistic breach conditions
        # Look for conditional language and realistic triggers
        plausible_indicators = ['if', 'when', 'given', 'assuming', 'should',
                               'were to', 'in case of']
        plausible_count = 0
        for cf in counterfactuals:
            breach = cf.get("breach_condition", "").lower()
            if any(indicator in breach for indicator in plausible_indicators):
                plausible_count += 1
        scores['plausibility'] = (plausible_count / len(counterfactuals)) * 10

        # 2. Specificity: Detailed breach conditions (>10 words minimum)
        specific_count = sum(
            1 for cf in counterfactuals
            if len(cf.get("breach_condition", "").split()) >= 10
        )
        scores['specificity'] = (specific_count / len(counterfactuals)) * 10

        # 3. Consequences: Multiple cascading effects
        avg_consequence_count = sum(
            len(cf.get("consequences", [])) for cf in counterfactuals
        ) / len(counterfactuals)
        # Normalize: 3+ consequences = full score
        scores['consequences'] = min((avg_consequence_count / 3) * 10, 10)

        # 4. Diversity: Cover different strategic axes
        axes = set(cf.get("axis", "") for cf in counterfactuals)
        expected_axes = {'escalation', 'containment', 'diplomatic',
                        'economic', 'internal', 'wildcard'}
        axis_coverage = len(axes & expected_axes) / len(expected_axes)
        scores['diversity'] = axis_coverage * 10

        overall_score = sum(scores.values()) / len(scores)
        return round(overall_score, 2)

    @staticmethod
    def evaluate_trajectories(trajectories: List[Dict[str, Any]]) -> float:
        """
        Score strategic outcome quality on 0-10 scale
        Metrics: coherence, quantification, timeline, decision_points
        """
        if not trajectories:
            return 0.0

        scores = {
            'coherence': 0.0,
            'quantification': 0.0,
            'timeline': 0.0,
            'decision_points': 0.0
        }

        # 1. Coherence: Logical progression
        coherent_count = sum(
            1 for traj in trajectories
            if 'description' in traj and len(traj.get('description', '')) > 50
        )
        scores['coherence'] = (coherent_count / len(trajectories)) * 10

        # 2. Quantification: Probability and severity scores present
        quantified_count = sum(
            1 for traj in trajectories
            if all(key in traj for key in ['probability', 'severity', 'confidence'])
        )
        scores['quantification'] = (quantified_count / len(trajectories)) * 10

        # 3. Timeline: Temporal progression defined
        timeline_count = sum(
            1 for traj in trajectories
            if 'timeline' in traj or 'timeframe' in traj
        )
        scores['timeline'] = (timeline_count / len(trajectories)) * 10

        # 4. Decision Points: Intervention opportunities identified
        decision_count = sum(
            len(traj.get('decision_points', [])) for traj in trajectories
        )
        avg_decisions = decision_count / len(trajectories)
        # Normalize: 2+ decision points = full score
        scores['decision_points'] = min((avg_decisions / 2) * 10, 10)

        overall_score = sum(scores.values()) / len(scores)
        return round(overall_score, 2)


class ExpertReview:
    """Human expert review integration"""

    @staticmethod
    def create_review_form(scenario_id: str, results: Dict[str, Any]) -> Dict:
        """Generate expert review form"""
        return {
            'scenario_id': scenario_id,
            'timestamp': None,  # Will be set when submitted
            'results_summary': {
                'assumption_count': len(results.get('assumptions', [])),
                'question_count': len(results.get('questions', [])),
                'counterfactual_count': len(results.get('counterfactuals', []))
            },
            'questions': [
                {
                    'id': 'q1',
                    'text': 'Are the identified assumptions comprehensive and accurate?',
                    'type': 'rating',
                    'scale': '1-5',
                    'required': True
                },
                {
                    'id': 'q2',
                    'text': 'Do the questions effectively challenge the assumptions?',
                    'type': 'rating',
                    'scale': '1-5',
                    'required': True
                },
                {
                    'id': 'q3',
                    'text': 'Are the counterfactuals plausible and valuable for strategic planning?',
                    'type': 'rating',
                    'scale': '1-5',
                    'required': True
                },
                {
                    'id': 'q4',
                    'text': 'What insights did this analysis reveal that traditional analysis would miss?',
                    'type': 'open_ended',
                    'required': True
                },
                {
                    'id': 'q5',
                    'text': 'What improvements would make this analysis more valuable?',
                    'type': 'open_ended',
                    'required': False
                }
            ]
        }

    @staticmethod
    def aggregate_reviews(reviews: List[Dict]) -> Dict:
        """Compile expert feedback into summary statistics"""
        if not reviews:
            return {'error': 'No reviews to aggregate'}

        ratings = {
            'q1_assumption_quality': [],
            'q2_question_quality': [],
            'q3_counterfactual_quality': []
        }

        insights = []
        improvements = []

        for review in reviews:
            for answer in review.get('answers', []):
                if answer['question_id'] == 'q1':
                    ratings['q1_assumption_quality'].append(answer['rating'])
                elif answer['question_id'] == 'q2':
                    ratings['q2_question_quality'].append(answer['rating'])
                elif answer['question_id'] == 'q3':
                    ratings['q3_counterfactual_quality'].append(answer['rating'])
                elif answer['question_id'] == 'q4':
                    insights.append(answer['text'])
                elif answer['question_id'] == 'q5':
                    improvements.append(answer['text'])

        return {
            'expert_count': len(reviews),
            'avg_assumption_rating': sum(ratings['q1_assumption_quality']) / len(ratings['q1_assumption_quality']),
            'avg_question_rating': sum(ratings['q2_question_quality']) / len(ratings['q2_question_quality']),
            'avg_counterfactual_rating': sum(ratings['q3_counterfactual_quality']) / len(ratings['q3_counterfactual_quality']),
            'overall_satisfaction': sum(
                sum(v) for v in ratings.values()
            ) / sum(len(v) for v in ratings.values()),
            'qualitative_insights': insights,
            'suggested_improvements': improvements
        }


if __name__ == "__main__":
    # Example usage
    sample_assumptions = [
        {
            "description": "Markets assume 3% annual GDP growth will continue",
            "domain": "economic",
            "confidence": 0.7
        },
        {
            "description": "Supply chains can be rapidly rerouted",
            "domain": "operational",
            "confidence": 0.5
        }
    ]

    score = QualityRubric.evaluate_assumptions(sample_assumptions)
    print(f"Assumption Quality Score: {score}/10")
