"""
Enhanced Phase 1: Surface Analysis API endpoints (Sprint 2).
Integrates all new services: extraction, categorization, scoring, relationships, synthesis, export.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from typing import Optional, List
import logging

from models.database import get_db
from models.user import User
from models.scenario import Scenario, SurfaceAnalysis
from schemas.scenario import SurfaceAnalysisResponse
from utils.auth import get_current_user

# Sprint 2 services
from services.assumption_extractor import AssumptionExtractor
from services.assumption_categorizer import AssumptionCategorizer
from services.quality_scorer import AssumptionQualityScorer
from services.relationship_detector import RelationshipDetector
from services.narrative_synthesizer import NarrativeSynthesizer
from services.export_formatter import ExportFormatter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{scenario_id}/surface-analysis-v2", response_model=SurfaceAnalysisResponse)
async def create_surface_analysis_v2(
    scenario_id: uuid.UUID,
    validate_consistency: bool = Query(default=True, description="Run consistency validation"),
    detect_relationships: bool = Query(default=True, description="Detect assumption relationships"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive surface analysis (Sprint 2 enhanced version).

    This endpoint orchestrates the full Sprint 2 pipeline:
    1. Extract assumptions with consistency validation
    2. Categorize into domains
    3. Score quality and assign priorities
    4. Detect relationships (optional)
    5. Synthesize baseline narrative
    """
    try:
        # Verify scenario ownership
        scenario = db.query(Scenario).filter(
            Scenario.id == scenario_id,
            Scenario.user_id == current_user.id
        ).first()

        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found"
            )

        logger.info(f"Starting Sprint 2 surface analysis for scenario {scenario_id}")

        # Step 1: Extract assumptions
        logger.info("Step 1: Extracting assumptions...")
        extractor = AssumptionExtractor()
        extraction_result = await extractor.extract(
            scenario.description,
            validate_consistency=validate_consistency
        )

        assumptions = extraction_result["assumptions"]
        metadata = extraction_result["metadata"]

        logger.info(f"Extracted {len(assumptions)} assumptions")

        if not assumptions:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No assumptions could be extracted from the scenario"
            )

        # Step 2: Categorize assumptions
        logger.info("Step 2: Categorizing assumptions...")
        categorizer = AssumptionCategorizer()
        assumptions = categorizer.categorize_batch(assumptions)

        # Step 3: Score quality
        logger.info("Step 3: Scoring assumption quality...")
        scorer = AssumptionQualityScorer()
        assumptions = scorer.score_batch(assumptions)

        # Step 4: Detect relationships (optional)
        relationships = None
        if detect_relationships:
            logger.info("Step 4: Detecting assumption relationships...")
            detector = RelationshipDetector()
            relationships = await detector.detect_relationships(assumptions)
        else:
            relationships = {
                "relationships": [],
                "graph_analysis": {},
                "statistics": {}
            }

        # Step 5: Synthesize baseline narrative
        logger.info("Step 5: Synthesizing baseline narrative...")
        synthesizer = NarrativeSynthesizer()
        narrative = await synthesizer.synthesize(
            scenario.description,
            assumptions,
            relationships
        )

        # Prepare complete analysis data
        analysis_data = {
            "assumptions": assumptions,
            "baseline_narrative": narrative.summary,
            "narrative_themes": narrative.themes,
            "anchor_assumptions": narrative.anchor_assumptions,
            "relationships": relationships,
            "metadata": {
                **metadata,
                "domain_distribution": categorizer.get_domain_distribution(assumptions),
                "priority_distribution": {
                    tier: len([a for a in assumptions if a.get("priority_tier") == tier])
                    for tier in ["high", "needs_review", "medium", "low"]
                }
            }
        }

        # Store surface analysis
        surface_analysis = SurfaceAnalysis(
            scenario_id=scenario_id,
            assumptions=analysis_data,  # Store complete analysis as JSONB
            baseline_narrative=narrative.summary
        )
        db.add(surface_analysis)
        db.commit()
        db.refresh(surface_analysis)

        logger.info(f"Surface analysis complete for scenario {scenario_id}")

        return surface_analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in surface analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing surface analysis: {str(e)}"
        )


@router.get("/{scenario_id}/surface-analysis-v2", response_model=SurfaceAnalysisResponse)
async def get_surface_analysis_v2(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get surface analysis for a scenario."""
    # Verify scenario ownership
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get surface analysis
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found. Please generate it first."
        )

    return surface_analysis


@router.get("/{scenario_id}/assumptions/filter")
async def filter_assumptions(
    scenario_id: uuid.UUID,
    domains: Optional[List[str]] = Query(None, description="Filter by domains"),
    priority: Optional[str] = Query(None, description="Filter by priority tier"),
    min_quality: Optional[float] = Query(None, description="Minimum quality score"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Filter and search assumptions by various criteria.

    Args:
        scenario_id: Scenario UUID
        domains: List of domains to filter by
        priority: Priority tier (high, medium, low, needs_review)
        min_quality: Minimum quality score (0-100)
    """
    # Verify scenario ownership
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get surface analysis
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found"
        )

    # Extract assumptions from JSONB
    assumptions = surface_analysis.assumptions.get("assumptions", [])

    # Apply filters
    filtered = assumptions

    if domains:
        filtered = [
            a for a in filtered
            if any(d in a.get("domains", []) for d in domains)
        ]

    if priority:
        filtered = [
            a for a in filtered
            if a.get("priority_tier") == priority
        ]

    if min_quality is not None:
        filtered = [
            a for a in filtered
            if a.get("quality_score", 0) >= min_quality
        ]

    return {
        "scenario_id": str(scenario_id),
        "total_assumptions": len(assumptions),
        "filtered_assumptions": len(filtered),
        "assumptions": filtered
    }


@router.get("/{scenario_id}/export/json")
async def export_json(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export surface analysis as JSON."""
    # Verify scenario ownership
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get surface analysis
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found"
        )

    # Format export
    formatter = ExportFormatter()

    scenario_dict = {
        "id": str(scenario.id),
        "title": scenario.title,
        "description": scenario.description,
        "created_at": scenario.created_at.isoformat(),
        "user_id": str(scenario.user_id)
    }

    analysis_data = surface_analysis.assumptions
    assumptions = analysis_data.get("assumptions", [])
    metadata = analysis_data.get("metadata", {})
    relationships = analysis_data.get("relationships", {})
    narrative = {
        "summary": surface_analysis.baseline_narrative,
        "themes": analysis_data.get("narrative_themes", []),
        "anchor_assumptions": analysis_data.get("anchor_assumptions", [])
    }

    json_export = formatter.export_json(
        scenario_dict,
        assumptions,
        metadata,
        relationships,
        narrative
    )

    return Response(
        content=json_export,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=scenario_{scenario_id}_analysis.json"
        }
    )


@router.get("/{scenario_id}/export/markdown")
async def export_markdown(
    scenario_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export surface analysis as Markdown report."""
    # Verify scenario ownership
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get surface analysis
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found"
        )

    # Format export
    formatter = ExportFormatter()

    scenario_dict = {
        "id": str(scenario.id),
        "title": scenario.title,
        "description": scenario.description,
        "created_at": scenario.created_at.isoformat(),
        "user_id": str(scenario.user_id)
    }

    analysis_data = surface_analysis.assumptions
    assumptions = analysis_data.get("assumptions", [])
    metadata = analysis_data.get("metadata", {})
    relationships = analysis_data.get("relationships", {})
    narrative = {
        "summary": surface_analysis.baseline_narrative,
        "themes": analysis_data.get("narrative_themes", []),
        "anchor_assumptions": analysis_data.get("anchor_assumptions", [])
    }

    markdown_export = formatter.export_markdown(
        scenario_dict,
        assumptions,
        metadata,
        relationships,
        narrative
    )

    return Response(
        content=markdown_export,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=scenario_{scenario_id}_analysis.md"
        }
    )


@router.post("/{scenario_id}/assumptions/validate")
async def validate_assumptions(
    scenario_id: uuid.UUID,
    assumption_updates: List[dict],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Batch validate/update assumptions.

    Body format:
    [
        {"assumption_id": "assumption_1", "action": "accept"},
        {"assumption_id": "assumption_2", "action": "reject"},
        {"assumption_id": "assumption_3", "action": "edit", "new_text": "Updated text"}
    ]
    """
    # Verify scenario ownership
    scenario = db.query(Scenario).filter(
        Scenario.id == scenario_id,
        Scenario.user_id == current_user.id
    ).first()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    # Get surface analysis
    surface_analysis = db.query(SurfaceAnalysis).filter(
        SurfaceAnalysis.scenario_id == scenario_id
    ).first()

    if not surface_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surface analysis not found"
        )

    # Update assumptions
    analysis_data = surface_analysis.assumptions
    assumptions = analysis_data.get("assumptions", [])

    for update in assumption_updates:
        assumption_id = update.get("assumption_id")
        action = update.get("action")

        for i, assumption in enumerate(assumptions):
            if assumption["id"] == assumption_id:
                if action == "accept":
                    assumptions[i]["validated"] = True
                elif action == "reject":
                    assumptions.pop(i)
                    break
                elif action == "edit":
                    assumptions[i]["text"] = update.get("new_text", assumption["text"])
                    assumptions[i]["user_edited"] = True
                    assumptions[i]["validated"] = True

    # Update database
    analysis_data["assumptions"] = assumptions
    surface_analysis.assumptions = analysis_data
    db.commit()

    return {
        "message": f"Updated {len(assumption_updates)} assumptions",
        "total_assumptions": len(assumptions)
    }
