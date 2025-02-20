from contextlib import asynccontextmanager

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from Backend.DB import get_db, init_db
from Backend.routers import user, physical, blood, sleep


@asynccontextmanager
async def lifespan(app: FastAPI):
    # set up the database
    load_dotenv()
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

"""
The routes are organized into separate routers for each data type (user, physical, blood, sleep). This separation helps
to keep the codebase organized and maintainable, especially as the application grows in complexity.
Like the Databases the routes are similar in structure and implementation, but again there is no real reason for that. 
That's is why there is no Unifying super class for the routes.
"""
app.include_router(user.router)
app.include_router(physical.router)
app.include_router(blood.router)
app.include_router(sleep.router)

def get_age_range(age: int) -> range:
    if age < 0:
        raise ValueError("Age cannot be negative")
    elif age <= 1:
        return range(0, 1)  # 0-1 baby
    elif age <= 3:
        return range(1, 4)  # 1-3 toddler
    elif age <= 12:
        return range(4, 13)  # 4-12 child
    elif age <= 19:
        return range(13, 20)  # 13-19 teen
    elif age <= 25:
        return range(20, 25)  # 20-25 young adult
    elif age <= 35:
        return range(25, 36)  # 25-35
    elif age <= 45:
        return range(36, 50)  # 36-45
    elif age <= 65:
        return range(51, 66)  # 51-65
    elif age <= 75:
        return range(66, 76)  # 66-75
    else:
        return range(76, 120)  # Arbitrary upper limit for seniors


def exponential_weighted_average(series: np.ndarray, base=2):
    # Generate exponential weights
    weights = np.arange(len(series))
    base = np.full_like(weights, base)
    np.power(base, weights, out=weights)

    # Calculate the weighted average
    weighted_avg = np.sum(series * weights) / np.sum(weights)

    return weighted_avg


@app.get('/get_health_score/{user_name}')
def get_health_score(user_name: str, db: Session = Depends(get_db)):
    """
    Get the health score of a user based on their physical, sleep and blood data.
    The health score itself is kind of nonsense, but it's a simple way to combine the three data types into one value,
    While giving more weight to more recent data.
    """
    user_data = user.get_user(user_name, db)
    age_range = get_age_range(user_data.age)
    try:
        physical_by_month = physical.get_avg_monthly(user_name, db)
        sleep_by_month = sleep.get_avg_monthly(user_name, db)
        blood_by_month = blood.get_avg_monthly(user_name, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # getting weighted average of the physical, sleep and blood data so more recent data has more weight
    physicals = [exponential_weighted_average(activity) for activity in physical_by_month]
    sleeps = [exponential_weighted_average(data) for data in sleep_by_month]
    bloods = [exponential_weighted_average(count) for count in blood_by_month]

    # summing the weighted averages and calculating the health score based on the average of the three
    physical_score = sum(physicals)
    sleep_score = sum(sleeps)
    blood_score = sum(bloods)
    calculated_score = (physical_score + sleep_score + blood_score) / 3

    # getting the average of all users in the same age range to compare the user's health score to the average
    all_avg_physical = physical.get_avg_all(age_range, db)
    all_avg_sleep = sleep.get_avg_all(age_range, db)
    all_avg_blood = blood.get_avg_all(age_range, db)

    # summing the averages of all users in the same age range and calculating the health score based on the average
    # No need for weighted average here as we are comparing the user to the average of all users in the same age range
    physical_score_all = sum(all_avg_physical)
    sleep_score_all = sum(all_avg_sleep)
    blood_score_all = sum(all_avg_blood)
    calculated_score_all = (physical_score_all.sum() + sleep_score_all.sum() + blood_score_all.sum()) / 3

    final_score:float = 100 * (calculated_score / calculated_score_all)

    return {'health_score': final_score}


@app.get("/")
def root():
    return {"message": "Health Tracker API Root"}
