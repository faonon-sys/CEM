"""
Sprint 3 - Phase 2 Deep Questioning API Endpoints (Enhanced)

Comprehensive API for the Deep Questioning Framework including:
- Scenario input validation
- Question generation
- Response capture
- Fragility analysis
- Export and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from models.database import get_db
from models.scenario import Scenario, SurfaceAnalysis
from models.user import User
from utils.auth import get_current_user
from services.assumption_validator import validator
from services.question_generator import question_engine
from services.fragility_detector import fragility_detector
from pydantic import BaseModel

router = APIRouter(prefix="/api/scenarios", tags=["deep_questions_v2"])
logger = logging.getLogger(__name__)


# ==================== Request/Response Models ====================

class ScenarioValidationRequest(BaseModel):
    scenario_text: str


class AssumptionValidationRequest(BaseModel):
    actions: List[dict]  # [{"assumption_id": "...", "action": "accept|reject|edit", "new_text": "..."}]


class QuestionGenerationRequest(BaseModel):
    max_questions: int = 10
    dimension_filter: Optional[str] = None
    validate_consistency: bool = True


class QuestionResponseSubmission(BaseModel):
    question_id: str
    response_text: str
    confidence: float  # 0-1


class FragilityAnalysisRequest(BaseModel):
    responses: List[QuestionResponseSubmission]


# ==================== Task 9: Scenario Input & Validation ====================

@router.post("/{scenario_id}/validate-input")
async def validate_scenario_input(
    scenario_id: str,
    request: ScenarioValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate scenario input text before processing.

    Returns validation results, warnings, and metadata.
    """
    try:
        validation = validator.validate_scenario_text(request.scenario_text)

        # Get inline assumption preview
        inline_assumptions = validator.extract_inline_assumptions(request.scenario_text)

        # Suggest domain tags
        domain_suggestions = validator.suggest_domain_tags(request.scenario_text)

        return {
            "validation": validation,
            "inline_assumptions_preview": inline_assumptions,
            "suggested_domains": domain_suggestions,
            "message": "Validation complete" if validation["valid"] else "Validation failed"
        }

    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_scenario_templates():
    """Get available scenario templates for quick start."""
    templates = validator.get_all_templates()
    return {
        "templates": templates,
        "count": len(templates)
    }


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get specific scenario template."""
    template = validator.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


# ==================== Task 1 & 2: Question Generation ====================

@router.post("/{scenario_id}/generate-questions")
async def generate_deep_questions(
    scenario_id: str,
    request: QuestionGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate contextually relevant deep questions for a scenario.

    Uses Phase 1 surface analysis results to generate probing questions
    across four dimensions: temporal, structural, actor-based, resource-based.
    """
    # Get scenario and surface analysis
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get surface analysis
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).order_by(SurfaceAnalysis.created_at.desc()).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=400,
            detail="No surface analysis found. Run Phase 1 first."
        )

    try:
        # Extract assumptions from surface analysis
        assumptions_data = surface_analysis.assumptions.get("assumptions", [])

        # Generate questions
        result = await question_engine.generate_questions(
            scenario_text=scenario.description,
            assumptions=assumptions_data,
            max_questions=request.max_questions,
            dimension_filter=request.dimension_filter
        )

        logger.info(f"Generated {len(result['questions'])} questions for scenario {scenario_id}")

        return {
            "scenario_id": scenario_id,
            "questions": result["questions"],
            "metadata": result["generation_metadata"],
            "total_generated": result["total_generated"],
            "dimension_distribution": _count_by_dimension(result["questions"])
        }

    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _count_by_dimension(questions: List[dict]) -> dict:
    """Count questions by dimension."""
    counts = {}
    for q in questions:
        dim = q["dimension"]
        counts[dim] = counts.get(dim, 0) + 1
    return counts


# ==================== Task 3: Fragility Analysis ====================

@router.post("/{scenario_id}/analyze-fragility")
async def analyze_fragility(
    scenario_id: str,
    request: FragilityAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze user responses to questions and identify fragility points.

    Returns:
    - Fragility scores for assumptions (1-10 scale)
    - Breach probabilities
    - Evidence gaps
    - Impact radius (cascading effects)
    """
    # Get scenario
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get surface analysis for assumptions
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).order_by(SurfaceAnalysis.created_at.desc()).first()

    if not surface_analysis:
        raise HTTPException(status_code=400, detail="No surface analysis found")

    try:
        assumptions = surface_analysis.assumptions.get("assumptions", [])
        dependency_graph = surface_analysis.assumptions.get("relationships", {})

        # Format responses for analysis
        questions_and_responses = []
        for resp in request.responses:
            # In a full implementation, we'd look up the question details
            # For now, create simplified structure
            questions_and_responses.append({
                "question": {"question_id": resp.question_id, "assumption_ids": []},
                "response": {
                    "text": resp.response_text,
                    "confidence": resp.confidence
                }
            })

        # Run fragility analysis
        analysis = fragility_detector.analyze_responses(
            questions_and_responses=questions_and_responses,
            assumptions=assumptions,
            dependency_graph=dependency_graph
        )

        logger.info(f"Fragility analysis complete: {analysis['summary']['fragilities_found']} fragilities found")

        return {
            "scenario_id": scenario_id,
            "fragility_analysis": analysis,
            "recommendations": _generate_recommendations(analysis)
        }

    except Exception as e:
        logger.error(f"Fragility analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_recommendations(analysis: dict) -> List[str]:
    """Generate actionable recommendations based on fragility analysis."""
    recommendations = []

    summary = analysis.get("summary", {})
    critical_count = summary.get("critical_count", 0)
    high_count = summary.get("high_count", 0)

    if critical_count > 0:
        recommendations.append(
            f"🚨 {critical_count} critical fragility point(s) identified. "
            "Immediate attention required - these assumptions could fail catastrophically."
        )

    if high_count > 0:
        recommendations.append(
            f"⚠️  {high_count} high-severity fragility point(s) detected. "
            "Develop contingency plans for these assumptions."
        )

    fragilities = analysis.get("fragility_points", [])

    # Check for assumptions with large impact radius
    high_impact = [f for f in fragilities if len(f.get("impact_radius", [])) > 3]
    if high_impact:
        recommendations.append(
            f"🔗 {len(high_impact)} assumption(s) have large impact radius. "
            "Failure would cascade through multiple dependent assumptions."
        )

    # Check for evidence gaps
    gaps = sum(len(f.get("evidence_gaps", [])) for f in fragilities)
    if gaps > 5:
        recommendations.append(
            f"📊 {gaps} evidence gap(s) identified. "
            "Gather additional data to strengthen these assumptions."
        )

    if not recommendations:
        recommendations.append("✅ No critical fragilities detected. Assumptions appear well-supported.")

    return recommendations


# ==================== Task 5: Validation & Export ====================

@router.post("/{scenario_id}/assumptions/validate-batch")
async def validate_assumptions_batch(
    scenario_id: str,
    request: AssumptionValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Batch validate assumptions (accept/reject/edit).
    """
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).order_by(SurfaceAnalysis.created_at.desc()).first()

    if not surface_analysis:
        raise HTTPException(status_code=404, detail="No surface analysis found")

    try:
        assumptions = surface_analysis.assumptions.get("assumptions", [])

        # Process validation actions
        updated_assumptions, stats = validator.validate_assumption_batch(
            assumptions=assumptions,
            actions=request.actions
        )

        # Update database
        surface_analysis.assumptions["assumptions"] = updated_assumptions
        db.commit()

        logger.info(f"Batch validation complete: {stats}")

        return {
            "scenario_id": scenario_id,
            "statistics": stats,
            "updated_count": len(updated_assumptions),
            "message": "Validation actions applied successfully"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Batch validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scenario_id}/deep-analysis/export")
async def export_deep_analysis(
    scenario_id: str,
    format: str = Query("json", regex="^(json|markdown)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export deep questioning analysis in various formats.

    Formats:
    - json: Structured data for system consumption
    - markdown: Human-readable report
    """
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get all analysis data
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).order_by(SurfaceAnalysis.created_at.desc()).first()

    if not surface_analysis:
        raise HTTPException(status_code=404, detail="No analysis data found")

    try:
        if format == "json":
            return {
                "scenario": {
                    "id": scenario.id,
                    "title": scenario.title,
                    "description": scenario.description
                },
                "surface_analysis": surface_analysis.assumptions,
                "export_timestamp": surface_analysis.created_at.isoformat()
            }
        else:  # markdown
            markdown = _generate_markdown_report(scenario, surface_analysis)
            return {
                "format": "markdown",
                "content": markdown
            }

    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_markdown_report(scenario: Scenario, analysis: SurfaceAnalysis) -> str:
    """Generate markdown report for deep questioning analysis."""
    assumptions = analysis.assumptions.get("assumptions", [])

    report = f"""# Deep Questioning Analysis: {scenario.title}

## Scenario Overview
{scenario.description[:500]}...

## Analysis Summary
- **Total Assumptions**: {len(assumptions)}
- **Analysis Date**: {analysis.created_at.strftime('%Y-%m-%d %H:%M')}

## Assumptions Identified

"""

    for i, assumption in enumerate(assumptions[:10], 1):
        report += f"""### {i}. {assumption.get('text', 'N/A')}

- **Domains**: {', '.join(assumption.get('domains', []))}
- **Confidence**: {assumption.get('confidence', 0) * 100:.1f}%
- **Quality Score**: {assumption.get('quality_score', 0):.1f}/100

"""

    report += f"\n\n*Report generated on {analysis.created_at.isoformat()}*\n"

    return report


# ==================== Health Check ====================

@router.get("/deep-questions/health")
async def health_check():
    """Health check for deep questioning services."""
    return {
        "status": "healthy",
        "services": {
            "validator": "operational",
            "question_engine": "operational",
            "fragility_detector": "operational"
        },
        "version": "2.0.0"
    }
