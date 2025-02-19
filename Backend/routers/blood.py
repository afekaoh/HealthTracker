import logging
from datetime import date
from typing import Annotated

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, BeforeValidator
from sqlalchemy import and_, select, update, delete
from sqlalchemy.orm import Session

from Backend.DB import get_db, BloodTest
from Backend.routers.user import get_user
from Backend.routers.utilities import validate_date_format, FilterParams, \
    DeleteParams

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/blood",
    tags=["blood"],
    responses={404: {"description": "Not found"}},
)


class UserBlood(BaseModel):
    user_id: int = Field(title="The id of the user", ge=0)
    RBC: float = Field(title="Red Blood Cell count", ge=0)
    WBC: float = Field(title="White Blood Cell count", ge=0)
    glucose_level: float = Field(title="The glucose level in the blood", ge=0)
    cholesterol_level: float = Field(title="The cholesterol level in the blood", ge=0)
    triglycerides_level: float = Field(title="The triglycerides level in the blood", ge=0)
    test_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the blood test')


@router.post('/')
def create_blood_test(blood_test: UserBlood, db: Session = Depends(get_db)):
    id = blood_test.user_id
    user = get_user(id, db)
    blood_db = BloodTest(
        user_id=blood_test.user_id,
        RBC=blood_test.RBC,
        WBC=blood_test.WBC,
        glucose_level=blood_test.glucose_level,
        cholesterol_level=blood_test.cholesterol_level,
        triglycerides_level=blood_test.triglycerides_level,
        date=blood_test.test_date
    )
    db.add(blood_db)
    db.commit()
    return {'message': f'Created Blood test to user {user.name} on {blood_test.test_date}'}


@router.get('/{user_id}')
def get_blood_tests(user_id: int,
                    query: Annotated[FilterParams, Query()] = None,
                    db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    details = 'No Blood test found for this user'
    if query.filter_by_date and query.filter_last:
        raise ValueError('Only one filter can be applied at a time')
    elif query.filter_last:
        select_query = select(BloodTest).where(BloodTest.user_id == user_id).order_by(
            BloodTest.date.desc()).limit(1)
    elif query.filter_by_date:
        select_query = select(BloodTest).where(and_(BloodTest.user_id == user_id,
                                                    BloodTest.date.in_(set(query.filter_by_date)))
                                               )
        details += f' on provided dates'
    else:
        select_query = select(BloodTest).where(BloodTest.user_id == user_id)
    blood_test = db.execute(select_query).scalars().all()
    if not blood_test:
        raise HTTPException(status_code=404, detail=details)
    response = [{
        'RBC'                : data.RBC,
        'WBC'                : data.WBC,
        'Glucose Level'      : data.glucose_level,
        'Cholesterol Level'  : data.cholesterol_level,
        'Triglycerides Level': data.triglycerides_level,
        'date'               : data.date
    } for data in blood_test]

    return {'user': user.name, 'blood_tests': response}


@router.put('/{user_id}')
def update_blood_test(user_id: int, blood: UserBlood, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    blood_test = db.execute(update(BloodTest).where(and_(BloodTest.user_id == user_id,
                                                         BloodTest.date == blood.test_date)).values(
        RBC=blood.RBC,
        WBC=blood.WBC,
        glucose_level=blood.glucose_level,
        cholesterol_level=blood.cholesterol_level,
        triglycerides_level=blood.triglycerides_level
    ))
    if blood_test.rowcount == 0:
        raise ValueError('No blood test found for this date')
    db.commit()
    return {'message': f'Updated Blood test for user {user.name} on {blood.test_date}'}


@router.delete('/{user_id}')
def delete_blood_test(user_id: int,
                      query: Annotated[DeleteParams, Query()],
                      db: Session = Depends(get_db)):
    if not query.delete_all and not query.delete_dates:
        raise ValueError('No delete parameters provided')
    user = get_user(user_id, db)
    if query.delete_all:
        delete_query = delete(BloodTest).where(BloodTest.user_id == user_id)
    else:
        delete_query = delete(BloodTest).where(
            and_(BloodTest.user_id == user_id,
                 BloodTest.date.in_(set(query.delete_dates))
                 )
        )
    result = db.execute(delete_query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='No blood test found to delete')
    db.commit()
    return {'message': f'Deleted Blood tests for user {user.name}'}


def get_avg_monthly(user_id: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    db = get_db()
    user = get_user(user_id, db)
    select_query = select(BloodTest).where(BloodTest.user_id == user_id).all()
    blood_tests = pd.read_sql(select_query, db.bind)
    blood_tests['date'] = pd.to_datetime(blood_tests['date'])
    blood_tests['date'] = blood_tests['date'].dt.month
    avgs = blood_tests.groupby(['date']).mean()
    RBC = avgs['RBC'].values
    WBC = avgs['WBC'].values
    glucose_level = avgs['glucose_level'].values
    cholesterol_level = avgs['cholesterol_level'].values
    triglycerides_level = avgs['triglycerides_level'].values
    return RBC, WBC, glucose_level, cholesterol_level, triglycerides_level


def get_avg_all() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    db = get_db()
    select_query = select(BloodTest).all()
    blood_tests = pd.read_sql(select_query, db.bind)
    blood_tests['date'] = pd.to_datetime(blood_tests['date'])
    blood_tests['date'] = blood_tests['date'].dt.month
    avgs = blood_tests.groupby(['user_id', 'date']).mean()
    RBC = avgs['RBC'].values
    WBC = avgs['WBC'].values
    glucose_level = avgs['glucose_level'].values
    cholesterol_level = avgs['cholesterol_level'].values
    triglycerides_level = avgs['triglycerides_level'].values
    return RBC, WBC, glucose_level, cholesterol_level, triglycerides_level
