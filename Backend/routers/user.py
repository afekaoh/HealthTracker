from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging
from Backend.DB import get_db, User, delete_all_data

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
class UserCreate(BaseModel):
    name: str = Field(title="The name of the user", max_length=30)
    age: int = Field(title="The age of the user", description='must be above 18', ge=18)


@router.post('/')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, age=user.age)
    db.add(db_user)
    db.commit()
    return {'message': f'User {user.name} created successfully', 'user_id': db_user.id}


@router.get('/{user_id}')
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return {'id': user.id, 'name': user.name, 'age': user.age}


@router.put('/{user_id}')
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    db_user.name = user.name
    db_user.age = user.age
    db.commit()
    return {'message': f'User {user.name} updated successfully'}


@router.delete('/{user_id}')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    name = db_user.name
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    delete_all_data(db, user_id)
    db.commit()
    return {'message': f'User {name} was deleted successfully with all related data'}