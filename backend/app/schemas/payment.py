from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.payment import PaymentType, PaymentStatus


# Payment schemas
class PaymentCreate(BaseModel):
    payment_type: PaymentType
    amount: float
    poll_id: Optional[int] = None
    description: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    poll_id: Optional[int] = None
    payment_type: PaymentType
    status: PaymentStatus
    amount: float
    currency: str
    stripe_payment_intent_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Payout schemas
class PayoutRequest(BaseModel):
    amount: float
    payout_method: str  # paypal, stripe, bank_transfer
    payout_email: Optional[str] = None


class PayoutResponse(BaseModel):
    id: int
    panel_member_id: int
    amount: float
    currency: str
    status: PaymentStatus
    payout_method: str
    payout_email: Optional[str] = None
    requested_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Wallet Transaction schema
class WalletTransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: float
    balance_after: float
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
