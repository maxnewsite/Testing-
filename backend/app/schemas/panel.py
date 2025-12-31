from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Panel Demographic schemas
class PanelDemographicCreate(BaseModel):
    category: str
    value: str


class PanelDemographicResponse(BaseModel):
    id: int
    category: str
    value: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Panel Member schemas
class PanelMemberBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    location_country: Optional[str] = None
    location_state: Optional[str] = None
    location_city: Optional[str] = None
    zip_code: Optional[str] = None


class PanelMemberCreate(PanelMemberBase):
    user_id: int


class PanelMemberUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    location_country: Optional[str] = None
    location_state: Optional[str] = None
    location_city: Optional[str] = None
    zip_code: Optional[str] = None


class PanelMemberResponse(PanelMemberBase):
    id: int
    user_id: int
    is_qualified: bool
    qualification_level: int
    is_suspended: bool
    total_responses: int
    total_earnings: float
    average_quality_score: float
    response_rate: float
    completion_rate: float
    wallet_balance: float
    joined_at: datetime
    last_active_at: Optional[datetime] = None
    profile_completeness: float
    demographics: List[PanelDemographicResponse] = []

    class Config:
        from_attributes = True


# Qualification schemas
class QualificationResponse(BaseModel):
    id: int
    qualification_type: str
    qualification_name: str
    is_passed: bool
    score: Optional[float] = None
    taken_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
