from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    panel_member_id = Column(Integer, ForeignKey("panel_members.id"), nullable=False)

    # Timing metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)

    # Status
    is_complete = Column(Boolean, default=False)
    is_validated = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)

    # Quality metrics
    quality_score = Column(Float, default=0.0)  # 0-100
    passed_attention_checks = Column(Boolean, default=True)
    response_speed_score = Column(Float, default=0.0)  # Consistency of timing
    consistency_score = Column(Float, default=0.0)  # Internal consistency

    # Compensation
    is_paid = Column(Boolean, default=False)
    payment_amount = Column(Float, nullable=True)

    # Metadata
    user_agent = Column(String)
    ip_address = Column(String)
    metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    poll = relationship("Poll", back_populates="responses")
    panel_member = relationship("PanelMember", back_populates="responses")
    answers = relationship(
        "ResponseAnswer", back_populates="response", cascade="all, delete-orphan"
    )
    quality_scores = relationship(
        "ResponseQualityScore", back_populates="response", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Response {self.id} for Poll {self.poll_id}>"


class ResponseAnswer(Base):
    __tablename__ = "response_answers"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    # Answer content
    answer_text = Column(Text, nullable=True)
    answer_choice = Column(String, nullable=True)  # For multiple choice
    answer_data = Column(JSON, nullable=True)  # For complex answers (rankings, etc.)

    # Metadata
    time_spent_seconds = Column(Integer, nullable=True)
    revision_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    response = relationship("Response", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    def __repr__(self):
        return f"<ResponseAnswer {self.id} for Question {self.question_id}>"


class ResponseQualityScore(Base):
    __tablename__ = "response_quality_scores"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)

    # Different quality dimensions
    attention_score = Column(Float, default=0.0)  # Based on attention checks
    speed_score = Column(Float, default=0.0)  # Not too fast, not too slow
    consistency_score = Column(Float, default=0.0)  # Internal consistency
    completion_score = Column(Float, default=0.0)  # Completeness of responses
    engagement_score = Column(Float, default=0.0)  # Depth of open-ended responses

    # Overall
    overall_score = Column(Float, default=0.0)

    # Fraud detection
    is_suspicious = Column(Boolean, default=False)
    fraud_indicators = Column(JSON, default=list)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    response = relationship("Response", back_populates="quality_scores")

    def __repr__(self):
        return f"<QualityScore {self.overall_score:.1f} for Response {self.response_id}>"
