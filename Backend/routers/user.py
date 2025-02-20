from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from Backend.DB import get_db, User

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


class UserCreate(BaseModel):
    user_name: str = Field(title="The name of the user", max_length=30)
    name: str = Field(title="The name of the user", max_length=30)
    age: int = Field(title="The age of the user", description='must be above 18', ge=18)


class UserUpdate(BaseModel):
    name: str = Field(title="The name of the user", max_length=30, default=None)
    age: int = Field(title="The age of the user", description='must be above 18', ge=18, default=None)


def get_user(user_name: str, db: Session) -> User:
    user = db.execute(select(User).where(User.user_name == user_name)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.post('/')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = get_user(user.user_name, db)
    except HTTPException as e:
        existing_user = None
    if existing_user:
        raise HTTPException(status_code=400, detail='User with this user_name already exists')
    db_user = User(user_name=user.user_name, name=user.name, age=user.age)
    db.add(db_user)
    db.commit()
    return {'message': f'User {user.name} created successfully', 'user_name': db_user.user_name}


@router.get('/{user_name}')
def get_user_endpoint(user_name: str, db: Session = Depends(get_db)):
    user = get_user(user_name, db)
    return {'user_name': user.user_name, 'name': user.name, 'age': user.age}


@router.put('/{user_name}')
def update_user(user_name: str, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = get_user(user_name, db)
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    user_id: int = db_user.id
    name = user.name or db_user.name
    age = user.age or db_user.age
    # there should be a check here to see if there were no changes to the user data, but for simplicity, I'll skip it
    update_query = update(User).where(User.id == user_id).values(name=name, age=age)
    db.execute(update_query)
    db.commit()
    return {'message': f'User {user.name} updated successfully'}


@router.delete('/{user_name}')
def delete_user(user_name: str, db: Session = Depends(get_db)):
    db_user = get_user(user_name, db)
    name = db_user.name
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    user_id: int = db_user.id
    delete_statement = delete(User).where(User.id == user_id)
    result = db.execute(delete_statement)  # This will delete all related data as well due to the CASCADE constraint
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='unexpected error occurred, user was not deleted successfully')
    db.commit()
    return {'message': f'User {name} was deleted successfully with all related data'}
