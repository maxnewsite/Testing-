from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.poll import Poll, Question
from app.models.response import Response, ResponseAnswer

router = APIRouter()


@router.get("/polls/{poll_id}/summary")
def get_poll_analytics_summary(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get analytics summary for a poll."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    # Verify ownership
    if current_user.role == UserRole.CLIENT and poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Get responses
    responses = db.query(Response).filter(Response.poll_id == poll_id).all()

    # Calculate metrics
    total_responses = len(responses)
    completed_responses = len([r for r in responses if r.is_complete])
    validated_responses = len([r for r in responses if r.is_validated])
    flagged_responses = len([r for r in responses if r.is_flagged])

    avg_quality_score = (
        sum(r.quality_score for r in responses) / total_responses if total_responses > 0 else 0
    )

    avg_time_seconds = (
        sum(r.time_spent_seconds for r in responses if r.time_spent_seconds)
        / completed_responses
        if completed_responses > 0
        else 0
    )

    return {
        "poll_id": poll_id,
        "total_responses": total_responses,
        "completed_responses": completed_responses,
        "validated_responses": validated_responses,
        "flagged_responses": flagged_responses,
        "completion_rate": (completed_responses / total_responses * 100)
        if total_responses > 0
        else 0,
        "average_quality_score": round(avg_quality_score, 2),
        "average_time_minutes": round(avg_time_seconds / 60, 2),
        "target_responses": poll.target_responses,
        "progress_percentage": (total_responses / poll.target_responses * 100)
        if poll.target_responses > 0
        else 0,
    }


@router.get("/polls/{poll_id}/questions/{question_id}/results")
def get_question_results(
    poll_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get aggregated results for a specific question."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    # Verify ownership
    if current_user.role == UserRole.CLIENT and poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    question = db.query(Question).filter(Question.id == question_id).first()

    if not question or question.poll_id != poll_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    # Get all answers for this question
    answers = (
        db.query(ResponseAnswer)
        .join(Response)
        .filter(
            ResponseAnswer.question_id == question_id,
            Response.is_complete == True,
            Response.is_validated == True,
        )
        .all()
    )

    # Aggregate results based on question type
    if question.question_type.value in ["ab_test", "multiple_choice", "image_choice"]:
        # Count choices
        choice_counts = {}
        for answer in answers:
            choice = answer.answer_choice or answer.answer_text
            if choice:
                choice_counts[choice] = choice_counts.get(choice, 0) + 1

        total = len(answers)
        results = [
            {
                "choice": choice,
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0,
            }
            for choice, count in choice_counts.items()
        ]

        return {
            "question_id": question_id,
            "question_text": question.text,
            "question_type": question.question_type,
            "total_responses": total,
            "results": sorted(results, key=lambda x: x["count"], reverse=True),
        }

    elif question.question_type.value == "rating_scale":
        # Calculate average rating
        ratings = [
            float(answer.answer_text or answer.answer_choice or 0) for answer in answers if answer.answer_text or answer.answer_choice
        ]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            "question_id": question_id,
            "question_text": question.text,
            "question_type": question.question_type,
            "total_responses": len(ratings),
            "average_rating": round(avg_rating, 2),
            "min_rating": min(ratings) if ratings else 0,
            "max_rating": max(ratings) if ratings else 0,
        }

    elif question.question_type.value == "open_ended":
        # Return text responses (could add sentiment analysis here)
        text_responses = [
            {
                "id": answer.id,
                "text": answer.answer_text,
                "time_spent_seconds": answer.time_spent_seconds,
            }
            for answer in answers
            if answer.answer_text
        ]

        return {
            "question_id": question_id,
            "question_text": question.text,
            "question_type": question.question_type,
            "total_responses": len(text_responses),
            "responses": text_responses,
        }

    else:
        return {
            "question_id": question_id,
            "question_text": question.text,
            "question_type": question.question_type,
            "total_responses": len(answers),
            "raw_data": [
                {
                    "answer_text": a.answer_text,
                    "answer_choice": a.answer_choice,
                    "answer_data": a.answer_data,
                }
                for a in answers
            ],
        }


@router.get("/polls/{poll_id}/export")
def export_poll_results(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export poll results (CSV format data)."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()

    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    # Verify ownership
    if current_user.role == UserRole.CLIENT and poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Get all responses with answers
    responses = (
        db.query(Response)
        .filter(Response.poll_id == poll_id, Response.is_complete == True)
        .all()
    )

    export_data = []
    for response in responses:
        row = {
            "response_id": response.id,
            "submitted_at": response.submitted_at.isoformat() if response.submitted_at else None,
            "time_spent_seconds": response.time_spent_seconds,
            "quality_score": response.quality_score,
            "is_validated": response.is_validated,
            "is_flagged": response.is_flagged,
        }

        # Add answers
        for answer in response.answers:
            question = answer.question
            column_name = f"q{question.order}_{question.question_type.value}"
            row[column_name] = answer.answer_text or answer.answer_choice or str(
                answer.answer_data
            )

        export_data.append(row)

    return {
        "poll_id": poll_id,
        "poll_title": poll.title,
        "export_data": export_data,
        "total_rows": len(export_data),
    }


@router.get("/dashboard")
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get dashboard metrics for current user."""
    if current_user.role == UserRole.CLIENT:
        # Client dashboard
        polls = db.query(Poll).filter(Poll.owner_id == current_user.id).all()

        total_polls = len(polls)
        active_polls = len([p for p in polls if p.status.value == "active"])
        total_responses = sum(p.response_count for p in polls)
        total_spent = sum(
            p.response_count * p.cost_per_response for p in polls if p.response_count > 0
        )

        return {
            "user_type": "client",
            "total_polls": total_polls,
            "active_polls": active_polls,
            "total_responses_collected": total_responses,
            "total_spent": round(total_spent, 2),
        }

    elif current_user.role == UserRole.PANELIST:
        # Panel member dashboard
        from app.models.panel import PanelMember

        panel_member = (
            db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()
        )

        if not panel_member:
            return {"error": "Panel member profile not found"}

        return {
            "user_type": "panelist",
            "total_responses": panel_member.total_responses,
            "total_earnings": round(panel_member.total_earnings, 2),
            "wallet_balance": round(panel_member.wallet_balance, 2),
            "average_quality_score": round(panel_member.average_quality_score, 2),
            "completion_rate": round(panel_member.completion_rate, 2),
            "qualification_level": panel_member.qualification_level,
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dashboard not available for this user type",
        )
