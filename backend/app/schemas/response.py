from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Response Answer schemas
class ResponseAnswerBase(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    answer_choice: Optional[str] = None
    answer_data: Optional[Dict[str, Any]] = None


class ResponseAnswerCreate(ResponseAnswerBase):
    time_spent_seconds: Optional[int] = None


class ResponseAnswerResponse(ResponseAnswerBase):
    id: int
    response_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Response schemas
class ResponseCreate(BaseModel):
    poll_id: int


class ResponseSubmit(BaseModel):
    response_id: int
    answers: List[ResponseAnswerCreate]
    time_spent_seconds: int
    metadata: Dict[str, Any] = {}


class ResponseResponse(BaseModel):
    id: int
    poll_id: int
    panel_member_id: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_spent_seconds: Optional[int] = None
    is_complete: bool
    is_validated: bool
    is_flagged: bool
    quality_score: float
    is_paid: bool
    payment_amount: Optional[float] = None
    answers: List[ResponseAnswerResponse] = []

    class Config:
        from_attributes = True


# Quality score schema
class QualityScoreResponse(BaseModel):
    attention_score: float
    speed_score: float
    consistency_score: float
    completion_score: float
    engagement_score: float
    overall_score: float
    is_suspicious: bool
    fraud_indicators: List[str]

    class Config:
        from_attributes = True
