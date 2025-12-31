from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User
from app.models.poll import Poll, Question, PollStatus
from app.schemas.poll import (
    PollCreate,
    PollUpdate,
    PollResponse,
    PollListResponse,
    QuestionCreate,
    QuestionResponse,
)

router = APIRouter()


@router.post("/", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
def create_poll(
    poll_data: PollCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new poll."""
    # Create poll
    poll = Poll(
        owner_id=current_user.id,
        title=poll_data.title,
        description=poll_data.description,
        target_responses=poll_data.target_responses,
        cost_per_response=poll_data.cost_per_response,
        estimated_duration_minutes=poll_data.estimated_duration_minutes,
        targeting_rules=poll_data.targeting_rules,
        status=PollStatus.DRAFT,
    )

    db.add(poll)
    db.flush()  # Get poll ID without committing

    # Create questions
    for question_data in poll_data.questions:
        question = Question(
            poll_id=poll.id,
            question_type=question_data.question_type,
            order=question_data.order,
            text=question_data.text,
            description=question_data.description,
            options=question_data.options,
            media_urls=question_data.media_urls,
            is_required=question_data.is_required,
            validation_rules=question_data.validation_rules,
            is_attention_check=question_data.is_attention_check,
            expected_answer=question_data.expected_answer,
        )
        db.add(question)

    db.commit()
    db.refresh(poll)

    return poll


@router.get("/", response_model=List[PollListResponse])
def list_polls(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: PollStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List user's polls."""
    query = db.query(Poll).filter(Poll.owner_id == current_user.id)

    if status:
        query = query.filter(Poll.status == status)

    polls = query.order_by(Poll.created_at.desc()).offset(skip).limit(limit).all()

    return polls


@router.get("/{poll_id}", response_model=PollResponse)
def get_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific poll."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return poll


@router.patch("/{poll_id}", response_model=PollResponse)
def update_poll(
    poll_id: int,
    poll_data: PollUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a poll."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Update fields
    update_data = poll_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(poll, field, value)

    poll.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(poll)

    return poll


@router.post("/{poll_id}/publish", response_model=PollResponse)
def publish_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Publish a poll to make it active."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if poll.status != PollStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft polls can be published",
        )

    # Validate poll has questions
    if not poll.questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Poll must have at least one question",
        )

    poll.status = PollStatus.ACTIVE
    poll.published_at = datetime.utcnow()
    db.commit()
    db.refresh(poll)

    return poll


@router.post("/{poll_id}/pause", response_model=PollResponse)
def pause_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Pause an active poll."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if poll.status != PollStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active polls can be paused",
        )

    poll.status = PollStatus.PAUSED
    db.commit()
    db.refresh(poll)

    return poll


@router.delete("/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a poll (only if it's a draft)."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if poll.status != PollStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft polls can be deleted",
        )

    db.delete(poll)
    db.commit()

    return None
