import logging
from datetime import date
from typing import Annotated

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, BeforeValidator
from sqlalchemy import and_, select, delete, update
from sqlalchemy.orm import Session

from Backend.DB import get_db, SleepActivity
from Backend.routers.user import get_user
from Backend.routers.utilities import validate_date_format, FilterParams, \
    DeleteParams

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/sleep",
    tags=["sleep"],
    responses={404: {"description": "Not found"}},
)


class UserSleep(BaseModel):
    user_id: int = Field(title="The id of the user", ge=0)
    sleep_hours: float = Field(title="The number of hours the user slept", ge=0)
    avg_heart_rate: float = Field(title="The average heart rate during sleep", ge=0)
    avg_oxygen_level: float = Field(title="The average oxygen level during sleep", ge=0)
    sleep_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the sleep activity')


@router.post('/')
def create_blood_test(sleep_activity: UserSleep, db: Session = Depends(get_db)):
    id = sleep_activity.user_id
    user = get_user(id, db)
    sleep_db = SleepActivity(
        user_id=sleep_activity.user_id,
        sleep_hours=sleep_activity.sleep_hours,
        avg_heart_rate=sleep_activity.avg_heart_rate,
        avg_oxygen_level=sleep_activity.avg_oxygen_level,
        date=sleep_activity.sleep_date
    )
    db.add(sleep_db)
    db.commit()
    return {'message': f'Created Sleep activity to user {user.name} on {sleep_activity.sleep_date}'}


@router.get('/{user_id}')
def get_sleep_activities(user_id: int,
                         query: Annotated[FilterParams, Query()] = None,
                         db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    details = 'No sleep activity found for this user'
    if query.filter_by_date and query.filter_last:
        raise ValueError('Only one filter can be applied at a time')
    elif query.filter_last:
        select_query = select(SleepActivity).where(SleepActivity.user_id == user_id).order_by(
            SleepActivity.date.desc()).limit(1)

    elif query.filter_by_date:
        select_query = select(SleepActivity).where(and_(SleepActivity.user_id == user_id,
                                                        SleepActivity.date.in_(set(query.filter_by_date)))
                                                   )
        details += f' on provided dates'
    else:
        select_query = select(SleepActivity).where(SleepActivity.user_id == user_id)
    sleep_activity = db.execute(select_query).scalars().all()
    if not sleep_activity:
        raise HTTPException(status_code=404, detail=details)
    response = [{
        'sleep_hours'     : data.sleep_hours,
        'avg_heart_rate'  : data.avg_heart_rate,
        'avg_oxygen_level': data.avg_oxygen_level,
        'date'            : data.date
    } for data in sleep_activity]

    return {'user': user.name, 'sleep activity': response}


@router.put('/{user_id}')
def update_sleep(user_id: int, sleep: UserSleep, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    update_query = update(SleepActivity).where(and_(SleepActivity.user_id == user_id,
                                                    SleepActivity.date == sleep.sleep_date)).values(
        sleep_hours=sleep.sleep_hours,
        avg_heart_rate=sleep.avg_heart_rate,
        avg_oxygen_level=sleep.avg_oxygen_level
    )
    sleep_activity = db.execute(update_query)
    db.commit()
    if sleep_activity.rowcount == 0:
        raise HTTPException(status_code=404, detail='No sleep activity found for this date')
    return {'message': f'Updated sleep activity for user {user.name} on {sleep.sleep_date}'}


@router.delete('/{user_id}')
def delete_sleep(user_id: int,
                 query: Annotated[DeleteParams, Query()],
                 db: Session = Depends(get_db)):
    if not query.delete_all and not query.delete_dates:
        raise ValueError('No delete parameters provided')
    user = get_user(user_id, db)
    if query.delete_all:
        delete_query = delete(SleepActivity).where(SleepActivity.user_id == user_id)
    else:
        delete_query = delete(SleepActivity).where(
            and_(SleepActivity.user_id == user_id,
                 SleepActivity.date.in_(set(query.delete_dates))
                 )
        )
    result = db.execute(delete_query)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='No sleep activity found for the provided dates')
    return {'message': f'Deleted sleep activity for user {user.name}'}


def get_avg_monthly(user_id: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    db = get_db()
    user = get_user(user_id, db)
    select_query = select(SleepActivity).where(SleepActivity.user_id == user_id).all()
    sleep_activity = pd.read_sql(select_query, db.bind)
    sleep_activity['date'] = pd.to_datetime(sleep_activity['date'])
    sleep_activity['date'] = sleep_activity['date'].dt.month
    avgs = sleep_activity.groupby(['date']).mean()
    sleep_hours = avgs['sleep_hours'].values
    avg_heart_rate = avgs['avg_heart_rate'].values
    avg_oxygen_level = avgs['avg_oxygen_level'].values
    return sleep_hours, avg_heart_rate, avg_oxygen_level


def get_avg_all() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    db = get_db()
    select_query = select(SleepActivity).all()
    sleep_activity = pd.read_sql(select_query, db.bind)
    sleep_activity['date'] = pd.to_datetime(sleep_activity['date'])
    sleep_activity['date'] = sleep_activity['date'].dt.month
    avgs = sleep_activity.groupby(['user_id', 'date']).mean()
    sleep_hours = avgs['sleep_hours'].values
    avg_heart_rate = avgs['avg_heart_rate'].values
    avg_oxygen_level = avgs['avg_oxygen_level'].values
    return sleep_hours, avg_heart_rate, avg_oxygen_level
