from datetime import date
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def validate_date_format(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError('Invalid date format. Date should be in the format YYYY-MM-DD')


def validate_date_list_format(value: list[str]) -> list[date]:
    try:
        return [date.fromisoformat(d) for d in value]
    except ValueError:
        raise ValueError('Invalid date format. Date should be in the format YYYY-MM-DD')


def validate_bool(value: str) -> bool:
    try:
        return bool(value)
    except ValueError:
        raise ValueError('Must be True or False')


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}
    filter_by_date: Annotated[list[date], BeforeValidator(validate_date_list_format)] = Field(default=None,
                                                                                              title='Filter by dates')
    filter_last: Annotated[bool, BeforeValidator(validate_bool)] = Field(default=None, title='Filter by last')


class DeleteParams(BaseModel):
    model_config = {"extra": "forbid"}
    delete_all: Annotated[bool, BeforeValidator(validate_bool)] = Field(default=None, title='delete all data')
    delete_dates: Annotated[list[date], BeforeValidator(validate_date_list_format)] = Field(default=None,
                                                                                            title='delete by dates')
