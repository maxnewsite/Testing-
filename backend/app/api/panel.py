from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.panel import PanelMember, PanelDemographic
from app.schemas.panel import (
    PanelMemberCreate,
    PanelMemberUpdate,
    PanelMemberResponse,
    PanelDemographicCreate,
)
from app.schemas.payment import WalletTransactionResponse

router = APIRouter()


@router.post("/", response_model=PanelMemberResponse, status_code=status.HTTP_201_CREATED)
def create_panel_member(
    panel_data: PanelMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create panel member profile."""
    # Verify user is a panelist
    if current_user.role != UserRole.PANELIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only panelists can create panel profiles",
        )

    # Check if profile already exists
    existing = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Panel member profile already exists",
        )

    # Create panel member
    panel_member = PanelMember(
        user_id=current_user.id,
        date_of_birth=panel_data.date_of_birth,
        gender=panel_data.gender,
        location_country=panel_data.location_country,
        location_state=panel_data.location_state,
        location_city=panel_data.location_city,
        zip_code=panel_data.zip_code,
    )

    db.add(panel_member)
    db.commit()
    db.refresh(panel_member)

    return panel_member


@router.get("/me", response_model=PanelMemberResponse)
def get_my_panel_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's panel member profile."""
    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()

    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    return panel_member


@router.patch("/me", response_model=PanelMemberResponse)
def update_my_panel_profile(
    panel_data: PanelMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's panel member profile."""
    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()

    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    # Update fields
    update_data = panel_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(panel_member, field, value)

    db.commit()
    db.refresh(panel_member)

    return panel_member


@router.post("/me/demographics", status_code=status.HTTP_201_CREATED)
def add_demographic(
    demographic_data: PanelDemographicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add demographic information to panel profile."""
    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()

    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    # Check if demographic already exists
    existing = (
        db.query(PanelDemographic)
        .filter(
            PanelDemographic.panel_member_id == panel_member.id,
            PanelDemographic.category == demographic_data.category,
        )
        .first()
    )

    if existing:
        # Update existing
        existing.value = demographic_data.value
        db.commit()
        return {"message": "Demographic updated"}

    # Create new demographic
    demographic = PanelDemographic(
        panel_member_id=panel_member.id,
        category=demographic_data.category,
        value=demographic_data.value,
    )

    db.add(demographic)
    db.commit()

    return {"message": "Demographic added"}


@router.get("/me/wallet/transactions", response_model=List[WalletTransactionResponse])
def get_wallet_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get wallet transaction history."""
    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()

    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    return panel_member.wallet_transactions
