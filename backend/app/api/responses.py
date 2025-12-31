from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.poll import Poll, PollStatus
from app.models.response import Response, ResponseAnswer, ResponseQualityScore
from app.models.panel import PanelMember
from app.schemas.response import ResponseCreate, ResponseSubmit, ResponseResponse

router = APIRouter()


@router.post("/", response_model=ResponseResponse, status_code=status.HTTP_201_CREATED)
def start_response(
    response_data: ResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start a new response (for panel members)."""
    # Verify user is a panel member
    if current_user.role != UserRole.PANELIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only panel members can submit responses",
        )

    # Get panel member
    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()
    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    # Verify poll exists and is active
    poll = db.query(Poll).filter(Poll.id == response_data.poll_id).first()
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.status != PollStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Poll is not active",
        )

    # Check if user already responded
    existing_response = (
        db.query(Response)
        .filter(
            Response.poll_id == response_data.poll_id,
            Response.panel_member_id == panel_member.id,
        )
        .first()
    )
    if existing_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already responded to this poll",
        )

    # Create response
    response = Response(
        poll_id=response_data.poll_id,
        panel_member_id=panel_member.id,
        started_at=datetime.utcnow(),
    )

    db.add(response)
    db.commit()
    db.refresh(response)

    return response


@router.post("/submit", response_model=ResponseResponse)
def submit_response(
    submission: ResponseSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit completed response."""
    # Get response
    response = db.query(Response).filter(Response.id == submission.response_id).first()

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")

    # Verify ownership
    if response.panel_member.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if response.is_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response already submitted",
        )

    # Save answers
    for answer_data in submission.answers:
        answer = ResponseAnswer(
            response_id=response.id,
            question_id=answer_data.question_id,
            answer_text=answer_data.answer_text,
            answer_choice=answer_data.answer_choice,
            answer_data=answer_data.answer_data,
            time_spent_seconds=answer_data.time_spent_seconds,
        )
        db.add(answer)

    # Update response
    response.submitted_at = datetime.utcnow()
    response.time_spent_seconds = submission.time_spent_seconds
    response.is_complete = True
    response.metadata = submission.metadata

    # Calculate quality score (simplified version)
    quality_score = ResponseQualityScore(
        response_id=response.id,
        attention_score=100.0,  # Would calculate based on attention checks
        speed_score=80.0,  # Would calculate based on timing
        consistency_score=90.0,  # Would calculate based on answer patterns
        completion_score=100.0,  # All questions answered
        engagement_score=85.0,  # Based on open-ended response depth
        overall_score=91.0,  # Weighted average
    )
    db.add(quality_score)

    response.quality_score = quality_score.overall_score
    response.is_validated = quality_score.overall_score >= 70.0

    # Update poll response count
    poll = response.poll
    poll.response_count += 1
    db.commit()

    # Credit panelist wallet (in a real system, this would be more complex)
    if response.is_validated:
        response.payment_amount = poll.cost_per_response
        panel_member = response.panel_member
        panel_member.wallet_balance += poll.cost_per_response
        panel_member.total_earnings += poll.cost_per_response
        panel_member.total_responses += 1
        response.is_paid = True
        db.commit()

    db.refresh(response)
    return response


@router.get("/available", response_model=List[dict])
def get_available_polls(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get available polls for panel member."""
    if current_user.role != UserRole.PANELIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only panel members can view available polls",
        )

    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()
    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    # Get active polls that user hasn't responded to
    responded_poll_ids = (
        db.query(Response.poll_id).filter(Response.panel_member_id == panel_member.id).all()
    )
    responded_ids = [poll_id for (poll_id,) in responded_poll_ids]

    polls = (
        db.query(Poll)
        .filter(
            Poll.status == PollStatus.ACTIVE,
            Poll.response_count < Poll.target_responses,
            ~Poll.id.in_(responded_ids) if responded_ids else True,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": poll.id,
            "title": poll.title,
            "description": poll.description,
            "estimated_duration_minutes": poll.estimated_duration_minutes,
            "reward": poll.cost_per_response,
        }
        for poll in polls
    ]


@router.get("/{response_id}", response_model=ResponseResponse)
def get_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific response."""
    response = db.query(Response).filter(Response.id == response_id).first()

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")

    # Check authorization
    if current_user.role == UserRole.PANELIST:
        if response.panel_member.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.role == UserRole.CLIENT:
        if response.poll.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return response
