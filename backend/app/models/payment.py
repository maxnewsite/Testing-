from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Float,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaymentType(str, Enum):
    POLL_CREATION = "poll_creation"  # Client pays to create poll
    RESPONSE_CREDIT = "response_credit"  # Client buys response credits
    SUBSCRIPTION = "subscription"  # Monthly/annual subscription
    REFUND = "refund"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=True)

    # Payment details
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    amount = Column(Float, nullable=False)  # In USD
    currency = Column(String, default="USD")

    # Stripe integration
    stripe_payment_intent_id = Column(String, unique=True, nullable=True, index=True)
    stripe_charge_id = Column(String, unique=True, nullable=True)
    stripe_customer_id = Column(String, nullable=True)

    # Metadata
    description = Column(Text)
    metadata = Column(String)  # JSON string for additional data

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")
    poll = relationship("Poll", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.id}: {self.amount} {self.currency} ({self.status})>"


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    panel_member_id = Column(Integer, ForeignKey("panel_members.id"), nullable=False)

    # Payout details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    # Payment method
    payout_method = Column(String, nullable=False)  # paypal, stripe, bank_transfer
    payout_email = Column(String, nullable=True)
    payout_account_id = Column(String, nullable=True)

    # Stripe integration
    stripe_payout_id = Column(String, unique=True, nullable=True)
    stripe_transfer_id = Column(String, unique=True, nullable=True)

    # Timing
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Metadata
    notes = Column(Text)

    # Relationships
    panel_member = relationship("PanelMember", back_populates="payouts")

    def __repr__(self):
        return f"<Payout {self.id}: {self.amount} {self.currency} ({self.status})>"


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    panel_member_id = Column(Integer, ForeignKey("panel_members.id"), nullable=False)

    # Transaction details
    transaction_type = Column(String, nullable=False)  # credit, debit, bonus, penalty
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)

    # Reference
    reference_type = Column(String, nullable=True)  # response, payout, bonus
    reference_id = Column(Integer, nullable=True)

    # Description
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    panel_member = relationship("PanelMember", back_populates="wallet_transactions")

    def __repr__(self):
        return f"<WalletTransaction {self.transaction_type}: {self.amount}>"
