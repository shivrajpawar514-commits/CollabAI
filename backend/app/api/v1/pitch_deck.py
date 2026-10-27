import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.pitch_deck import HackathonPitchDeckResponse, ProjectPortfolioExportResponse
from app.services.pitch_deck_service import PitchDeckService

router = APIRouter(prefix="/projects", tags=["Pitch Deck & Portfolio Export"])
_pitch_service = PitchDeckService()


@router.get(
    "/{project_id}/pitch-deck",
    response_model=HackathonPitchDeckResponse,
    summary="Generate 7-slide Hackathon Pitch Deck",
)
async def generate_pitch_deck(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Synthesizes a 7-slide Hackathon Pitch Deck containing presenter scripts,
    slide titles, key architectural highlights, and visual suggestions.
    """
    deck = await _pitch_service.get_pitch_deck(project_id, db)
    return deck


@router.get(
    "/{project_id}/portfolio-export",
    response_model=ProjectPortfolioExportResponse,
    summary="Export project portfolio & Devpost README markdown",
)
async def export_project_portfolio(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a full-featured markdown portfolio export ready for Devpost submission
    or GitHub README showcasing.
    """
    return await _pitch_service.get_portfolio_export(project_id, db)
