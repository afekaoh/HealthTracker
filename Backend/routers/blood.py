from datetime import date
from typing import Annotated, Union

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, BeforeValidator
from sqlalchemy import and_, select, update, delete
from sqlalchemy.orm import Session

from Backend.DB import get_db, BloodTest, User
from Backend.routers.user import get_user
from Backend.routers.utilities import validate_date_format, FilterParams, \
    DeleteParams

router = APIRouter(
    prefix="/blood",
    tags=["blood"],
    responses={404: {"description": "Not found"}},
)


# Blood Test Models
class UserBlood(BaseModel):
    RBC: float = Field(title="Red Blood Cell count", ge=0)
    WBC: float = Field(title="White Blood Cell count", ge=0)
    glucose_level: float = Field(title="The glucose level in the blood", ge=0)
    cholesterol_level: float = Field(title="The cholesterol level in the blood", ge=0)
    triglycerides_level: float = Field(title="The triglycerides level in the blood", ge=0)
    test_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the blood test')


class UserBloodUpdate(BaseModel):
    # only the provided values will be updated
    RBC: Union[float, None] = Field(title="Red Blood Cell count", ge=0, default=None)
    WBC: Union[float, None] = Field(title="White Blood Cell count", ge=0, default=None)
    glucose_level: Union[float, None] = Field(title="The glucose level in the blood", ge=0, default=None)
    cholesterol_level: Union[float, None] = Field(title="The cholesterol level in the blood", ge=0, default=None)
    triglycerides_level: Union[float, None] = Field(title="The triglycerides level in the blood", ge=0, default=None)
    test_date: Annotated[date, BeforeValidator(validate_date_format)] = Field(title='The date of the blood test')


# CRUD Operations
@router.post('/{user_name}')
def create_blood_test(user_name: str, blood_test: UserBlood, db: Session = Depends(get_db)):
    user = get_user(user_name, db)
    user_id = user.id
    blood_db = BloodTest(
        user_id=user_id,
        RBC=blood_test.RBC,
        WBC=blood_test.WBC,
        glucose_level=blood_test.glucose_level,
        cholesterol_level=blood_test.cholesterol_level,
        triglycerides_level=blood_test.triglycerides_level,
        date=blood_test.test_date
    )
    blood = db.execute(
        select(BloodTest)
        .where(
            and_(BloodTest.user_id == user_id,
                 BloodTest.date == blood_test.test_date))
    ).scalar_one_or_none()
    if blood:
        raise HTTPException(status_code=400, detail='Blood test already exists for this date, use PUT to update it')
    db.add(blood_db)
    db.commit()
    return {'message': f'Created Blood test to user {user.name} on {blood_test.test_date}'}


@router.get('/{user_name}')
def get_blood_tests(user_name: str,
                    query: Annotated[FilterParams, Query()] = None,
                    db: Session = Depends(get_db)):
    user = get_user(user_name, db)
    user_id: int = user.id
    details = 'No Blood test found for this user'
    if query.filter_by_date and query.filter_last:
        raise HTTPException(status_code=400, detail='Only one filter can be applied at a time')
    elif query.filter_last:
        select_query = (select(BloodTest)
                        .where(BloodTest.user_id == user_id)
                        .order_by(BloodTest.date.desc())
                        .limit(1))
    elif query.filter_by_date:
        select_query = (select(BloodTest)
        .where(
            and_(
                BloodTest.user_id == user_id,
                BloodTest.date.in_(set(query.filter_by_date)))
        ))
        details += f' on the provided dates'
    else:
        # Get all blood tests
        select_query = select(BloodTest).where(BloodTest.user_id == user_id)
    blood_test = db.execute(select_query).scalars().all()
    if not blood_test:
        raise HTTPException(status_code=404, detail=details)
    # making the response more readable and make sure only the required fields are returned
    response = [{
        'RBC'                : data.RBC,
        'WBC'                : data.WBC,
        'Glucose Level'      : data.glucose_level,
        'Cholesterol Level'  : data.cholesterol_level,
        'Triglycerides Level': data.triglycerides_level,
        'date'               : data.date
    } for data in blood_test]

    return {'user': user.name, 'blood_tests': response}


@router.put('/{user_name}')
def update_blood_test(user_name: str, blood: UserBloodUpdate, db: Session = Depends(get_db)):
    user = get_user(user_name, db)
    user_id: int = user.id
    update_values = blood.dict(exclude={'test_date'}, exclude_none=True)  # update only the provided values
    blood_test = db.execute(update(BloodTest)
                            .where(
        and_(
            BloodTest.user_id == user_id,
            BloodTest.date == blood.test_date))
                            .values(**update_values))
    if blood_test.rowcount == 0:
        raise HTTPException(status_code=404, detail='No blood test found for this date')
    db.commit()
    return {'message': f'Updated Blood test for user {user.name} on {blood.test_date}'}


@router.delete('/{user_name}')
def delete_blood_test(user_name: str,
                      query: Annotated[DeleteParams, Query()],
                      db: Session = Depends(get_db)):
    if not query.delete_all and not query.delete_dates:
        raise HTTPException(status_code=400, detail='No delete parameters provided')
    user = get_user(user_name, db)
    user_id: int = user.id
    if query.delete_all:
        delete_query = delete(BloodTest).where(BloodTest.user_id == user_id)
    else:
        # delete only the provided dates, logic dictates that the user has provided the dates since query.delete_dates is not empty
        delete_query = (delete(BloodTest)
        .where(
            and_(
                BloodTest.user_id == user_id,
                BloodTest.date.in_(set(query.delete_dates)))))
    result = db.execute(delete_query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='No blood test found to delete')
    db.commit()
    return {'message': f'Deleted Blood tests for user {user.name}'}


def get_avg_monthly(user_name: str, db: Session) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Get the average blood test values for each month for a user
    the calculation itself is nonsense since it's just for demonstration purposes
    """
    user = get_user(user_name, db)
    user_id: int = user.id
    select_query = select(BloodTest).where(BloodTest.user_id == user_id)
    blood_tests = pd.read_sql(select_query, db.bind)
    if blood_tests.empty:
        raise ValueError('No blood tests found for this user')
    blood_tests['date'] = pd.to_datetime(blood_tests['date'])
    blood_tests['date'] = blood_tests['date'].dt.month
    avgs = blood_tests.groupby(['date']).mean()
    RBC = avgs['RBC'].values
    WBC = avgs['WBC'].values
    glucose_level = avgs['glucose_level'].values
    cholesterol_level = avgs['cholesterol_level'].values
    triglycerides_level = avgs['triglycerides_level'].values
    return RBC, WBC, glucose_level, cholesterol_level, triglycerides_level


def get_avg_all(age_range: range, db: Session) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Get the average blood test values for all users within a specific age range
    The calculation itself is nonsense since it's just for demonstration purposes
    """
    select_query = select(BloodTest).join(User).where(User.age.in_(age_range))
    blood_tests = pd.read_sql(select_query, db.bind)
    cols = ['user_id', 'RBC', 'WBC', 'glucose_level', 'cholesterol_level', 'triglycerides_level']
    blood_tests = blood_tests[cols]
    avgs = blood_tests.groupby(['user_id']).mean()
    RBC = avgs['RBC'].values
    WBC = avgs['WBC'].values
    glucose_level = avgs['glucose_level'].values
    cholesterol_level = avgs['cholesterol_level'].values
    triglycerides_level = avgs['triglycerides_level'].values
    return RBC, WBC, glucose_level, cholesterol_level, triglycerides_level
