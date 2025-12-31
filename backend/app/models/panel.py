from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Date,
    JSON,
    ForeignKey,
    Float,
    Text,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class PanelMember(Base):
    __tablename__ = "panel_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Profile
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    location_country = Column(String, nullable=True)
    location_state = Column(String, nullable=True)
    location_city = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)

    # Status
    is_qualified = Column(Boolean, default=False)
    qualification_level = Column(Integer, default=0)  # 0-5 tier system
    is_suspended = Column(Boolean, default=False)
    suspension_reason = Column(Text, nullable=True)

    # Performance metrics
    total_responses = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    average_quality_score = Column(Float, default=0.0)
    response_rate = Column(Float, default=0.0)  # Acceptance rate
    completion_rate = Column(Float, default=0.0)

    # Wallet
    wallet_balance = Column(Float, default=0.0)

    # Metadata
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=True)
    profile_completeness = Column(Float, default=0.0)  # 0-100%

    # Relationships
    user = relationship("User", back_populates="panel_member")
    demographics = relationship(
        "PanelDemographic", back_populates="panel_member", cascade="all, delete-orphan"
    )
    qualifications = relationship(
        "PanelQualification", back_populates="panel_member", cascade="all, delete-orphan"
    )
    responses = relationship("Response", back_populates="panel_member")
    wallet_transactions = relationship(
        "WalletTransaction", back_populates="panel_member", cascade="all, delete-orphan"
    )
    payouts = relationship("Payout", back_populates="panel_member")

    def __repr__(self):
        return f"<PanelMember {self.id} (User {self.user_id})>"


class PanelDemographic(Base):
    __tablename__ = "panel_demographics"

    id = Column(Integer, primary_key=True, index=True)
    panel_member_id = Column(Integer, ForeignKey("panel_members.id"), nullable=False)

    # Demographic category
    category = Column(String, nullable=False, index=True)  # e.g., "income", "education"
    value = Column(String, nullable=False)  # e.g., "$50k-$75k", "Bachelor's degree"

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    panel_member = relationship("PanelMember", back_populates="demographics")

    def __repr__(self):
        return f"<Demographic {self.category}: {self.value}>"


class PanelQualification(Base):
    __tablename__ = "panel_qualifications"

    id = Column(Integer, primary_key=True, index=True)
    panel_member_id = Column(Integer, ForeignKey("panel_members.id"), nullable=False)

    # Qualification details
    qualification_type = Column(String, nullable=False)  # e.g., "screening_survey"
    qualification_name = Column(String, nullable=False)
    data = Column(JSON, default=dict)  # Qualification-specific data

    # Status
    is_passed = Column(Boolean, default=False)
    score = Column(Float, nullable=True)

    # Timing
    taken_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    panel_member = relationship("PanelMember", back_populates="qualifications")

    def __repr__(self):
        return f"<Qualification {self.qualification_name} ({'Passed' if self.is_passed else 'Failed'})>"
