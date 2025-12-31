from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.payment import Payment, PaymentStatus, PaymentType, Payout, WalletTransaction
from app.models.panel import PanelMember
from app.schemas.payment import PaymentCreate, PaymentResponse, PayoutRequest, PayoutResponse
import stripe

router = APIRouter()

# Configure Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a payment intent for poll creation or credits."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can make payments",
        )

    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        poll_id=payment_data.poll_id,
        payment_type=payment_data.payment_type,
        amount=payment_data.amount,
        description=payment_data.description,
        status=PaymentStatus.PENDING,
    )

    db.add(payment)
    db.flush()

    # Create Stripe payment intent
    if settings.STRIPE_SECRET_KEY:
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment_data.amount * 100),  # Convert to cents
                currency="usd",
                metadata={
                    "payment_id": payment.id,
                    "user_id": current_user.id,
                },
            )
            payment.stripe_payment_intent_id = intent.id
        except stripe.error.StripeError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}",
            )

    db.commit()
    db.refresh(payment)

    return payment


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List user's payments."""
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )

    return payments


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail="Webhook secret not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle payment intent succeeded
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_id = payment_intent["metadata"].get("payment_id")

        if payment_id:
            payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()
            if payment:
                payment.status = PaymentStatus.COMPLETED
                payment.stripe_charge_id = payment_intent.get("charges", {}).get("data", [{}])[
                    0
                ].get("id")
                db.commit()

    return {"status": "success"}


@router.post("/payouts", response_model=PayoutResponse, status_code=status.HTTP_201_CREATED)
def request_payout(
    payout_data: PayoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Request a payout from wallet balance."""
    if current_user.role != UserRole.PANELIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only panel members can request payouts",
        )

    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()

    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    # Check wallet balance
    if panel_member.wallet_balance < payout_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance",
        )

    # Minimum payout check
    if payout_data.amount < 10.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum payout amount is $10",
        )

    # Create payout request
    payout = Payout(
        panel_member_id=panel_member.id,
        amount=payout_data.amount,
        payout_method=payout_data.payout_method,
        payout_email=payout_data.payout_email,
        status=PaymentStatus.PENDING,
    )

    db.add(payout)

    # Deduct from wallet
    panel_member.wallet_balance -= payout_data.amount

    # Create wallet transaction
    transaction = WalletTransaction(
        panel_member_id=panel_member.id,
        transaction_type="debit",
        amount=-payout_data.amount,
        balance_after=panel_member.wallet_balance,
        reference_type="payout",
        description=f"Payout request via {payout_data.payout_method}",
    )
    db.add(transaction)

    db.commit()
    db.refresh(payout)

    return payout


@router.get("/payouts", response_model=List[PayoutResponse])
def list_payouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List user's payout requests."""
    if current_user.role != UserRole.PANELIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only panel members can view payouts",
        )

    panel_member = db.query(PanelMember).filter(PanelMember.user_id == current_user.id).first()

    if not panel_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Panel member profile not found",
        )

    payouts = (
        db.query(Payout)
        .filter(Payout.panel_member_id == panel_member.id)
        .order_by(Payout.requested_at.desc())
        .all()
    )

    return payouts
