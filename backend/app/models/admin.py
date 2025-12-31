from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Float,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class FlaggedResponse(Base):
    __tablename__ = "flagged_responses"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False, unique=True)

    # Flag details
    flag_type = Column(String, nullable=False)  # quality, fraud, inappropriate, other
    flag_reason = Column(Text, nullable=False)
    auto_flagged = Column(Boolean, default=False)  # Was it flagged by algorithm?

    # Review status
    is_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_decision = Column(String, nullable=True)  # approved, rejected, requires_action
    review_notes = Column(Text, nullable=True)

    # Actions taken
    action_taken = Column(String, nullable=True)  # none, payment_withheld, user_warned, user_banned

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FlaggedResponse {self.id} ({self.flag_type})>"


class PanelHealthMetric(Base):
    __tablename__ = "panel_health_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Time period
    metric_date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String, default="daily")  # daily, weekly, monthly

    # Panel size metrics
    total_members = Column(Integer, default=0)
    active_members = Column(Integer, default=0)  # Active in period
    new_members = Column(Integer, default=0)
    churned_members = Column(Integer, default=0)

    # Activity metrics
    total_responses = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)  # In minutes
    completion_rate = Column(Float, default=0.0)  # Percentage

    # Quality metrics
    average_quality_score = Column(Float, default=0.0)
    flagged_responses = Column(Integer, default=0)
    fraudulent_responses = Column(Integer, default=0)

    # Financial metrics
    total_payouts = Column(Float, default=0.0)
    average_payout = Column(Float, default=0.0)

    # Demographics snapshot
    demographics_snapshot = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PanelHealthMetric {self.metric_date.date()} ({self.period_type})>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Action details
    action = Column(String, nullable=False, index=True)  # create_poll, flag_response, etc.
    resource_type = Column(String, nullable=False)  # poll, response, user, etc.
    resource_id = Column(Integer, nullable=True)

    # Changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    # Context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type}>"
