import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from Backend.DB import get_db, User

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


class UserCreate(BaseModel):
    name: str = Field(title="The name of the user", max_length=30)
    age: int = Field(title="The age of the user", description='must be above 18', ge=18)


def get_user(user_id: int, db: Session = None) -> User:
    if not db:
        db = get_db()
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.post('/')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, age=user.age)
    db.add(db_user)
    db.commit()
    return {'message': f'User {user.name} created successfully', 'user_id': db_user.id}


@router.get('/{user_id}')
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user(user_id, db)
    return {'id': user.id, 'name': user.name, 'age': user.age}


@router.put('/{user_id}')
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(user_id, db)
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    update_query = update(User).where(User.id == user_id).values(name=user.name, age=user.age)
    db.execute(update_query)
    db.commit()
    return {'message': f'User {user.name} updated successfully'}


@router.delete('/{user_id}')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(user_id, db)
    name = db_user.name
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    delete_statement = delete(User).where(User.id == user_id)
    result = db.execute(delete_statement)  # This will delete all related data as well due to the CASCADE constraint
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='unexpected error occurred, user was not deleted successfully')
    db.commit()
    return {'message': f'User {name} was deleted successfully with all related data'}
