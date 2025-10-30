# /backend/schemas.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import uuid


# --- PYDANTIC MODELS ---
class UserCreate(BaseModel):
    display_name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class DailyMetricData(BaseModel):
    metric_type: str
    metric_name: str
    value: int


class CompletedRoutineData(BaseModel):
    routine_id: uuid.UUID


class TopGoalData(BaseModel):
    goal_description: str
    is_completed: bool


class CompletedStepData(BaseModel):
    step_id: uuid.UUID
    is_completed: bool
    actual_duration: Optional[int] = None


class CheckinCreate(BaseModel):
    checkin_date: date = date.today()
    gratitude_entry: Optional[str] = None
    principle_alignment: Optional[int] = None
    principle_alignment_note: Optional[str] = None
    metrics: List[DailyMetricData] = []
    completed_steps: List[CompletedStepData] = []
    top_goal: Optional[TopGoalData] = None


class PersonalityTraitData(BaseModel):
    scale_name: str
    trait_name: str
    value: int
    display_order: int


class PersonalityUpdateRequest(BaseModel):
    traits: List[PersonalityTraitData]


class UserPrincipleData(BaseModel):
    principle_id: uuid.UUID
    rank: int


class PrincipleUpdateRequest(BaseModel):
    principles: List[UserPrincipleData]


class TopGoalUpdate(BaseModel):
    is_completed: bool


class RoutineCreate(BaseModel):
    routine_name: str


class RoutineStep(BaseModel):
    step_id: uuid.UUID
    routine_id: uuid.UUID
    step_name: str
    target_duration: Optional[int] = None
    step_order: int


class RoutineStepCreate(BaseModel):
    step_name: str
    target_duration: Optional[int] = None
    step_order: int


class Routine(BaseModel):
    routine_id: uuid.UUID
    routine_name: str
    is_active: bool
    created_at: datetime
    steps: List[RoutineStep] = []
