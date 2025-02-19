import logging
from datetime import date
from typing import Annotated, Union

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, BeforeValidator
from sqlalchemy import and_
from sqlalchemy.orm import Session

from Backend.DB import get_db, PhysicalActivity
from Backend.routers.user import get_user
from Backend.routers.utilities import validate_date_format, validate_bool, validate_date_list_format

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/physical",
    tags=["physical"],
    responses={404: {"description": "Not found"}},
)


class UserPhysical(BaseModel):
    user_id: int = Field(title="The id of the user", ge=0)
    steps: int = Field(title="The number of steps the user took in the day", ge=0)
    cardio_time_session_minutes: Union[int, None] = Field(default=None,
                                                          title='Cardio training time in minutes')  # Optional field
    strength_time_session_minutes: Union[int, None] = Field(default=None,
                                                            title='Strength training time in minutes')  # Optional field
    session_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the activity')


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


@router.post('/')
def create_physical(physical: UserPhysical, db: Session = Depends(get_db)):
    id = physical.user_id
    user = get_user(id, db)
    physical_db = PhysicalActivity(
        user_id=physical.user_id,
        steps=physical.steps,
        cardio_time_session_minutes=physical.cardio_time_session_minutes or 0,
        strength_time_session_minutes=physical.strength_time_session_minutes or 0,
        date=physical.session_date
    )
    db.add(physical_db)
    db.commit()
    return {'message': f'Created Physical data to user {user["name"]} on {physical.session_date}'}


@router.get('/{user_id}')
def get_physical_data(user_id: int,
                      query: Annotated[FilterParams, Query()] = None,
                      db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    if query.filter_by_date and query.filter_last:
        raise ValueError('Only one filter can be applied at a time')
    elif query.filter_last:
        physical_data = db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).order_by(
            PhysicalActivity.date.desc()).first()
        response = {
            'physical_data': {
                'steps'                        : physical_data.steps,
                'cardio_time_session_minutes'  : physical_data.cardio_time_session_minutes,
                'strength_time_session_minutes': physical_data.strength_time_session_minutes,
                'date'                         : physical_data.date,
            }
        }
    elif query.filter_by_date:
        physical_data = db.query(PhysicalActivity).filter(and_(PhysicalActivity.user_id == user_id,
                                                               PhysicalActivity.date in set(query.filter_by_date))
                                                          ).all()
        response = [{
            'steps'                        : data.steps,
            'cardio_time_session_minutes'  : data.cardio_time_session_minutes,
            'strength_time_session_minutes': data.strength_time_session_minutes,
            'date'                         : data.date
        } for data in physical_data]
    else:
        physical_data = db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).all()
        response = [{
            'steps'                        : data.steps,
            'cardio_time_session_minutes'  : data.cardio_time_session_minutes,
            'strength_time_session_minutes': data.strength_time_session_minutes,
            'date'                         : data.date
        } for data in physical_data]
    if not physical_data:
        raise HTTPException(status_code=404, detail='No physical data found')
    return {'user': user['name'], 'physical_data': response}


@router.put('/{user_id}')
def update_physical(user_id: int, physical: UserPhysical, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    physical_data = db.query(PhysicalActivity).filter(and_(PhysicalActivity.user_id == user_id,
                                                           PhysicalActivity.date == physical.session_date)).first()
    if not physical_data:
        raise ValueError('No physical data found for this date')
    physical_data.steps = physical.steps
    physical_data.cardio_time_session_minutes += physical.cardio_time_session_minutes or 0
    physical_data.strength_time_session_minutes += physical.strength_time_session_minutes or 0
    db.commit()
    return {'message': f'Updated Physical data for user {user["name"]} on {physical.session_date}'}


@router.delete('/{user_id}')
def delete_physical(user_id: int,
                    query: Annotated[DeleteParams, Query()],
                    db: Session = Depends(get_db)):
    if not query.delete_all and not query.delete_dates:
        raise ValueError('No delete parameters provided')

    user = get_user(user_id, db)
    if query.delete_all:
        db.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).delete()
    elif query.delete_dates:
        db.query(PhysicalActivity).filter(and_(PhysicalActivity.user_id == user_id,
                                               PhysicalActivity.date in set(query.delete_dates))).delete()
    db.commit()
    return {'message': f'Deleted Physical data for user {user["name"]}'}
