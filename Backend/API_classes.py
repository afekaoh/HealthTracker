from datetime import date

from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    name: str
    age: int


class UserPhysical(BaseModel):
    steps: int
    cardio_time_session_minutes: int
    strength_time_session_minutes: int
    session_date: date

    @field_validator('session_date', mode='before')
    def validate_date_format(value: str) -> date:
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError('Invalid date format. Date should be in the format YYYY-MM-DD')


class UserBlood(BaseModel):
    RBC: float
    WBC: float
    glucose_level: float
    cholesterol_level: float
    triglycerides_level: float
    test_date: date

    @field_validator('test_date', mode='before')
    def validate_date_format(value: str) -> date:
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError('Invalid date format. Date should be in the format YYYY-MM-DD')


class UserSleep(BaseModel):
    sleep_hours: float
    avg_heart_rate: float
    avg_oxygen_level: float
    sleep_date: date

    @field_validator('sleep_date', mode='before')
    def validate_date_format(value: str) -> date:
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError('Invalid date format. Date should be in the format YYYY-MM-DD')
