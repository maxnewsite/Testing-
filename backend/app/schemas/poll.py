from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.poll import PollStatus, QuestionType


# Question schemas
class QuestionBase(BaseModel):
    question_type: QuestionType
    text: str
    description: Optional[str] = None
    options: List[str] = []
    media_urls: List[str] = []
    is_required: bool = True
    validation_rules: Dict[str, Any] = {}
    is_attention_check: bool = False
    expected_answer: Optional[str] = None


class QuestionCreate(QuestionBase):
    order: int


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    description: Optional[str] = None
    options: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    is_required: Optional[bool] = None
    validation_rules: Optional[Dict[str, Any]] = None


class QuestionResponse(QuestionBase):
    id: int
    poll_id: int
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


# Poll schemas
class PollBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_responses: int = 50
    cost_per_response: float = 1.0
    estimated_duration_minutes: int = 5
    targeting_rules: Dict[str, Any] = {}


class PollCreate(PollBase):
    questions: List[QuestionCreate]


class PollUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PollStatus] = None
    target_responses: Optional[int] = None
    cost_per_response: Optional[float] = None
    targeting_rules: Optional[Dict[str, Any]] = None


class PollResponse(PollBase):
    id: int
    owner_id: int
    status: PollStatus
    response_count: int
    completion_rate: float
    average_quality_score: float
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True


# Poll list response (lighter version)
class PollListResponse(BaseModel):
    id: int
    title: str
    status: PollStatus
    target_responses: int
    response_count: int
    completion_rate: float
    created_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
