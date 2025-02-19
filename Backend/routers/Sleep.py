from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, BeforeValidator

from Backend.routers.utilities import validate_date_format


class UserSleep(BaseModel):
    user_id: int = Field(title="The id of the user", ge=0)
    sleep_hours: float = Field(title="The number of hours the user slept", ge=0)
    avg_heart_rate: float = Field(title="The average heart rate during sleep", ge=0)
    avg_oxygen_level: float = Field(title="The average oxygen level during sleep", ge=0)
    sleep_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the sleep activity')
