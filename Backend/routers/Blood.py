import logging
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, BeforeValidator
from sqlalchemy import and_
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
def create_physical(blood_test: UserBlood, db: Session = Depends(get_db)):
    id = blood_test.user_id
    user = get_user(id, db)
    blood_db = BloodTest(
        user_id=blood_test.user_id,

        date=blood_test.session_date
    )
    db.add(blood_db)
    db.commit()
    return {'message': f'Created Physical data to user {user["name"]} on {blood_test.session_date}'}


@router.get('/{user_id}')
def get_blood_tests(user_id: int,
                    query: Annotated[FilterParams, Query()] = None,
                    db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    if query.filter_by_date and query.filter_last:
        raise ValueError('Only one filter can be applied at a time')
    elif query.filter_last:
        blood_test = db.query(BloodTest).filter(BloodTest.user_id == user_id).order_by(
            BloodTest.date.desc()).first()
        response = {
            'Blood test': {
                'RBC'                : blood_test.RBC,
                'WBC'                : blood_test.WBC,
                'Glucose Level'      : blood_test.glucose_level,
                'Cholesterol Level'  : blood_test.cholesterol_level,
                'Triglycerides Level': blood_test.triglycerides_level,
                'date'               : blood_test.date
            }
        }
    elif query.filter_by_date:
        blood_test = db.query(BloodTest).filter(and_(BloodTest.user_id == user_id,
                                                     BloodTest.date in set(query.filter_by_date))
                                                ).all()
        response = [{
            'RBC'                : data.RBC,
            'WBC'                : data.WBC,
            'Glucose Level'      : data.glucose_level,
            'Cholesterol Level'  : data.cholesterol_level,
            'Triglycerides Level': data.triglycerides_level,
            'date'               : data.date
        } for data in blood_test]
    else:
        blood_test = db.query(BloodTest).filter(BloodTest.user_id == user_id).all()
        response = [{
            'RBC'                : data.RBC,
            'WBC'                : data.WBC,
            'Glucose Level'      : data.glucose_level,
            'Cholesterol Level'  : data.cholesterol_level,
            'Triglycerides Level': data.triglycerides_level,
            'date'               : data.date
        } for data in blood_test]
    if not blood_test:
        raise HTTPException(status_code=404, detail='No physical data found')
    return {'user': user['name'], 'blood_test': response}


@router.put('/{user_id}')
def update_physical(user_id: int, blood: UserBlood, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    blood_test = db.query(BloodTest).filter(and_(BloodTest.user_id == user_id,
                                                 BloodTest.date == blood.session_date)).first()
    if not blood_test:
        raise ValueError('No blood test found for this date')
    blood_test.RBC = blood.RBC
    blood_test.WBC = blood.WBC
    blood_test.glucose_level = blood.glucose_level
    blood_test.cholesterol_level = blood.cholesterol_level
    blood_test.triglycerides_level = blood.triglycerides_level
    db.commit()
    return {'message': f'Updated Blood test for user {user["name"]} on {blood.session_date}'}


@router.delete('/{user_id}')
def delete_user(user_id: int,
                query: Annotated[DeleteParams, Query()],
                db: Session = Depends(get_db)):
    if not query.delete_all and not query.delete_dates:
        raise ValueError('No delete parameters provided')
    user = get_user(user_id, db)
    if query.delete_all:
        db.query(BloodTest).filter(BloodTest.user_id == user_id).delete()
    elif query.delete_dates:
        db.query(BloodTest).filter(and_(BloodTest.user_id == user_id,
                                        BloodTest.date in set(query.delete_dates))).delete()
    db.commit()
    return {'message': f'Deleted Blood tests for user {user["name"]}'}
