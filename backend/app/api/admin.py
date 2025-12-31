from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.response import Response
from app.models.admin import FlaggedResponse, PanelHealthMetric
from app.models.panel import PanelMember
from app.models.payment import Payout, PaymentStatus

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/flagged-responses")
def list_flagged_responses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_reviewed: bool = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """List flagged responses for review."""
    query = db.query(FlaggedResponse)

    if is_reviewed is not None:
        query = query.filter(FlaggedResponse.is_reviewed == is_reviewed)

    flagged = query.order_by(FlaggedResponse.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": f.id,
            "response_id": f.response_id,
            "flag_type": f.flag_type,
            "flag_reason": f.flag_reason,
            "auto_flagged": f.auto_flagged,
            "is_reviewed": f.is_reviewed,
            "created_at": f.created_at,
        }
        for f in flagged
    ]


@router.post("/flagged-responses/{flagged_id}/review")
def review_flagged_response(
    flagged_id: int,
    decision: str,
    notes: str = None,
    action: str = "none",
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Review a flagged response."""
    from datetime import datetime

    flagged = db.query(FlaggedResponse).filter(FlaggedResponse.id == flagged_id).first()

    if not flagged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flagged response not found",
        )

    # Update flag
    flagged.is_reviewed = True
    flagged.reviewed_by = admin_user.id
    flagged.reviewed_at = datetime.utcnow()
    flagged.review_decision = decision
    flagged.review_notes = notes
    flagged.action_taken = action

    # Take action based on decision
    if decision == "rejected" and action == "payment_withheld":
        response = db.query(Response).filter(Response.id == flagged.response_id).first()
        if response and response.is_paid:
            # Reverse payment
            response.is_paid = False
            panel_member = response.panel_member
            if response.payment_amount:
                panel_member.wallet_balance -= response.payment_amount
                panel_member.total_earnings -= response.payment_amount

    db.commit()

    return {"message": "Review completed", "decision": decision, "action": action}


@router.get("/panel-health")
def get_panel_health_metrics(
    period_type: str = "daily",
    limit: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Get panel health metrics."""
    metrics = (
        db.query(PanelHealthMetric)
        .filter(PanelHealthMetric.period_type == period_type)
        .order_by(PanelHealthMetric.metric_date.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "date": m.metric_date.isoformat(),
            "total_members": m.total_members,
            "active_members": m.active_members,
            "new_members": m.new_members,
            "churned_members": m.churned_members,
            "total_responses": m.total_responses,
            "average_response_time": m.average_response_time,
            "completion_rate": m.completion_rate,
            "average_quality_score": m.average_quality_score,
            "flagged_responses": m.flagged_responses,
            "total_payouts": m.total_payouts,
        }
        for m in metrics
    ]


@router.get("/panel-members")
def list_panel_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_suspended: bool = None,
    min_quality_score: float = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """List panel members with filters."""
    query = db.query(PanelMember)

    if is_suspended is not None:
        query = query.filter(PanelMember.is_suspended == is_suspended)

    if min_quality_score is not None:
        query = query.filter(PanelMember.average_quality_score >= min_quality_score)

    members = query.offset(skip).limit(limit).all()

    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "total_responses": m.total_responses,
            "total_earnings": m.total_earnings,
            "average_quality_score": m.average_quality_score,
            "wallet_balance": m.wallet_balance,
            "is_qualified": m.is_qualified,
            "is_suspended": m.is_suspended,
            "joined_at": m.joined_at,
        }
        for m in members
    ]


@router.post("/panel-members/{member_id}/suspend")
def suspend_panel_member(
    member_id: int,
    reason: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Suspend a panel member."""
    member = db.query(PanelMember).filter(PanelMember.id == member_id).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member not found",
        )

    member.is_suspended = True
    member.suspension_reason = reason
    db.commit()

    return {"message": "Panel member suspended", "member_id": member_id}


@router.post("/panel-members/{member_id}/unsuspend")
def unsuspend_panel_member(
    member_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Unsuspend a panel member."""
    member = db.query(PanelMember).filter(PanelMember.id == member_id).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member not found",
        )

    member.is_suspended = False
    member.suspension_reason = None
    db.commit()

    return {"message": "Panel member unsuspended", "member_id": member_id}


@router.get("/payouts/pending")
def list_pending_payouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """List pending payout requests."""
    payouts = (
        db.query(Payout)
        .filter(Payout.status == PaymentStatus.PENDING)
        .order_by(Payout.requested_at)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": p.id,
            "panel_member_id": p.panel_member_id,
            "amount": p.amount,
            "payout_method": p.payout_method,
            "payout_email": p.payout_email,
            "requested_at": p.requested_at,
        }
        for p in payouts
    ]


@router.post("/payouts/{payout_id}/process")
def process_payout(
    payout_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Mark payout as processed."""
    from datetime import datetime

    payout = db.query(Payout).filter(Payout.id == payout_id).first()

    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found",
        )

    payout.status = PaymentStatus.COMPLETED
    payout.processed_at = datetime.utcnow()
    payout.completed_at = datetime.utcnow()

    db.commit()

    return {"message": "Payout processed", "payout_id": payout_id}


@router.get("/statistics")
def get_platform_statistics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Get overall platform statistics."""
    from app.models.poll import Poll

    total_users = db.query(func.count(User.id)).scalar()
    total_clients = db.query(func.count(User.id)).filter(User.role == UserRole.CLIENT).scalar()
    total_panelists = (
        db.query(func.count(User.id)).filter(User.role == UserRole.PANELIST).scalar()
    )
    total_polls = db.query(func.count(Poll.id)).scalar()
    total_responses = db.query(func.count(Response.id)).scalar()
    total_panel_members = db.query(func.count(PanelMember.id)).scalar()

    total_earnings = db.query(func.sum(PanelMember.total_earnings)).scalar() or 0
    total_wallet_balance = db.query(func.sum(PanelMember.wallet_balance)).scalar() or 0

    return {
        "total_users": total_users,
        "total_clients": total_clients,
        "total_panelists": total_panelists,
        "total_polls": total_polls,
        "total_responses": total_responses,
        "total_panel_members": total_panel_members,
        "total_earnings_paid": round(total_earnings, 2),
        "total_wallet_balance": round(total_wallet_balance, 2),
    }
