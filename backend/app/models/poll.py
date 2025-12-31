from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
    Float,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class PollStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class QuestionType(str, Enum):
    AB_TEST = "ab_test"  # Compare two options
    RANKING = "ranking"  # Rank multiple items
    OPEN_ENDED = "open_ended"  # Free text response
    MULTIPLE_CHOICE = "multiple_choice"
    RATING_SCALE = "rating_scale"
    IMAGE_CHOICE = "image_choice"
    VIDEO_RESPONSE = "video_response"


class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(PollStatus), default=PollStatus.DRAFT, nullable=False)

    # Configuration
    target_responses = Column(Integer, default=50)
    cost_per_response = Column(Float, default=1.0)  # In USD
    estimated_duration_minutes = Column(Integer, default=5)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Targeting
    targeting_rules = Column(JSON, default=dict)  # Demographics, behaviors, etc.

    # Analytics cache
    response_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    average_quality_score = Column(Float, default=0.0)

    # Relationships
    owner = relationship("User", back_populates="polls")
    questions = relationship(
        "Question", back_populates="poll", cascade="all, delete-orphan", order_by="Question.order"
    )
    responses = relationship("Response", back_populates="poll", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="poll")

    def __repr__(self):
        return f"<Poll {self.id}: {self.title} ({self.status})>"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    order = Column(Integer, nullable=False)

    # Content
    text = Column(Text, nullable=False)
    description = Column(Text)  # Additional context

    # Configuration
    options = Column(JSON, default=list)  # For multiple choice, ranking, etc.
    media_urls = Column(JSON, default=list)  # Images, videos
    is_required = Column(Boolean, default=True)

    # Validation rules
    validation_rules = Column(JSON, default=dict)  # Min/max length, patterns, etc.

    # Quality controls
    is_attention_check = Column(Boolean, default=False)
    expected_answer = Column(String, nullable=True)  # For attention checks

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    poll = relationship("Poll", back_populates="questions")
    answers = relationship("ResponseAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question {self.id}: {self.question_type} in Poll {self.poll_id}>"


class TargetingRule(Base):
    __tablename__ = "targeting_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    rule_type = Column(String, nullable=False)  # demographic, behavioral, custom
    rule_data = Column(JSON, nullable=False)  # Actual targeting criteria
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<TargetingRule {self.name}>"
