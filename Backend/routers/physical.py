from datetime import date
from typing import Annotated, Union

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, BeforeValidator
from sqlalchemy import and_, select, delete, update
from sqlalchemy.orm import Session

from Backend.DB import get_db, PhysicalActivity, User
from Backend.routers.user import get_user
from Backend.routers.utilities import validate_date_format, DeleteParams, \
    FilterParams

router = APIRouter(
    prefix="/physical",
    tags=["physical"],
    responses={404: {"description": "Not found"}},
)


class UserPhysical(BaseModel):
    steps: int = Field(title="The number of steps the user took in the day", ge=0)
    cardio_time_session_minutes: int = Field(default=0,
                                             title='Cardio training time in minutes')  # Optional field
    strength_time_session_minutes: int = Field(default=0,
                                               title='Strength training time in minutes')  # Optional field
    session_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the activity')


class UserPhysicalUpdate(BaseModel):
    # only the provided values will be updated
    steps: Union[int, None] = Field(default=None,
                                    title="The number of steps the user took in the day",
                                    ge=0)
    cardio_time_session_minutes: Union[int, None] = Field(default=None,
                                                          title='Cardio training time in minutes',
                                                          ge=0)
    strength_time_session_minutes: Union[int, None] = Field(default=None,
                                                            title='Strength training time in minutes',
                                                            ge=0)
    session_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the activity')


@router.post('/{user_name}')
def create_physical(user_name: str, physical: UserPhysical, db: Session = Depends(get_db)):
    user = get_user(user_name, db)
    user_id = user.id
    physical_db = PhysicalActivity(
        user_id=user_id,
        steps=physical.steps,
        cardio_time_session_minutes=physical.cardio_time_session_minutes,
        strength_time_session_minutes=physical.strength_time_session_minutes,
        date=physical.session_date
    )
    physical_data = db.execute(
        select(PhysicalActivity)
        .where(
            and_(PhysicalActivity.user_id == user_id,
                 PhysicalActivity.date == physical.session_date))
    ).scalar_one_or_none()
    if physical_data:
        raise HTTPException(status_code=400, detail='Physical data already exists for this date, use PUT to update it')
    db.add(physical_db)
    db.commit()
    return {'message': f'Created Physical data to user {user.name} on {physical.session_date}'}


@router.get('/{user_name}')
def get_physical_data(user_name: str,
                      query: Annotated[FilterParams, Query()] = None,
                      db: Session = Depends(get_db)):
    user = get_user(user_name, db)
    user_id: int = user.id
    details = 'No physical data found for this user'
    if query.filter_by_date and query.filter_last:
        raise HTTPException(status_code=400, detail='Only one filter can be applied at a time')
    elif query.filter_last:
        select_query = (select(PhysicalActivity)
                        .where(PhysicalActivity.user_id == user_id)
                        .order_by(PhysicalActivity.date.desc())
                        .limit(1))
    elif query.filter_by_date:
        select_query = (select(PhysicalActivity)
        .where(
            and_(
                PhysicalActivity.user_id == user_id,
                PhysicalActivity.date.in_(set(query.filter_by_date)))))
        details += ' on the provided dates'
    else:
        select_query = select(PhysicalActivity).where(PhysicalActivity.user_id == user_id)

    physical_data = db.execute(select_query).scalars().all()
    if not physical_data:
        raise HTTPException(status_code=404, detail=details)
    response = [{
        'steps'                        : data.steps,
        'cardio_time_session_minutes'  : data.cardio_time_session_minutes,
        'strength_time_session_minutes': data.strength_time_session_minutes,
        'date'                         : data.date
    } for data in physical_data]
    return {'user': user.name, 'physical_data': response}


@router.put('/{user_name}')
def update_physical(user_name: str, physical: UserPhysicalUpdate, db: Session = Depends(get_db)):
    user = get_user(user_name, db)
    user_id: int = user.id
    physical_data = db.execute(
        select(PhysicalActivity)
        .where(
            and_(
                PhysicalActivity.user_id == user_id,
                PhysicalActivity.date == physical.session_date))
        .limit(1)
    ).scalar_one_or_none()
    if not physical_data:
        raise HTTPException(status_code=404, detail='No physical data found for this date')
    update_values = physical.dict(exclude={'session_date'}, exclude_none=True)
    result = db.execute(
        update(PhysicalActivity)
        .where(
            and_(
                PhysicalActivity.user_id == user_id,
                PhysicalActivity.date == physical.session_date))
        .values(**update_values))
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='No physical data found for the provided dates')
    return {'message': f'Updated Physical data for user {user.name} on {physical.session_date}'}


@router.delete('/{user_name}')
def delete_physical(user_name: str,
                    query: Annotated[DeleteParams, Query()],
                    db: Session = Depends(get_db)):
    if not (query.delete_all or query.delete_dates):
        raise HTTPException(status_code=400, detail='No delete parameters provided')

    user = get_user(user_name, db)
    user_id: int = user.id
    if query.delete_all:
        delete_query = delete(PhysicalActivity).where(PhysicalActivity.user_id == user_id)
    else:
        delete_query = (delete(PhysicalActivity)
        .where(
            and_(
                PhysicalActivity.user_id == user_id,
                PhysicalActivity.date.in_(set(query.delete_dates)))))
    result = db.execute(delete_query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='No physical data found for the provided dates')
    db.commit()
    return {'message': f'Deleted Physical data for user {user.name}'}


def get_avg_monthly(user_name: str, db: Session) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    user = get_user(user_name, db)
    user_id: int = user.id
    select_query = select(PhysicalActivity).where(PhysicalActivity.user_id == user_id)
    physical_activity = pd.read_sql(select_query, db.bind)
    if physical_activity.empty:
        raise ValueError('No physical data found for this user')
    physical_activity['date'] = pd.to_datetime(physical_activity['date'])
    physical_activity['date'] = physical_activity['date'].dt.month
    avgs = physical_activity.groupby(['date']).mean()
    steps = avgs['steps'].values
    cardio = avgs['cardio_time_session_minutes'].values
    strength = avgs['strength_time_session_minutes'].values
    return steps, cardio, strength


def get_avg_all(age_range: range, db: Session) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    select_query = select(PhysicalActivity).join(User).where(User.age.in_(age_range))
    physical_activity = pd.read_sql(select_query, db.bind)
    cols = ['user_id', 'steps', 'cardio_time_session_minutes', 'strength_time_session_minutes']
    physical_activity = physical_activity[cols]
    avgs = physical_activity.groupby(['user_id']).mean()
    steps = avgs['steps'].values
    cardio = avgs['cardio_time_session_minutes'].values
    strength = avgs['strength_time_session_minutes'].values
    # return just the values for user data protection
    return steps, cardio, strength
