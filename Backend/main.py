import logging

import numpy as np
from fastapi import FastAPI

from Backend.routers import user, physical, blood, sleep

logger = logging.getLogger(__name__)  # logging.getLogger('uvicorn.error').setLevel(logging.ERROR)
app = FastAPI(debug=True)

"""````````````````````````
I've decided not to implement any security measures for this API, as it is a simple example and to implement those correctly would be byond the scope and hide the true intention of this exmple.
In a real-world scenario, I would implement security measures such as authentication and authorization.
I'll also add in comments where would I add security measures.

1. There should be authentication for the users, so only the users can access their data, 
   that should be done using a 3rd party service like OAuth2 and maybe another if we want to support regular logins.
2. each endpoint should have authorization to check if the user has the right to access the data.
3. The data should be encrypted in the database.
4. The data should be encrypted during transit by using TLS.
5. The API should have rate limiting.

Implimation notes:
1. For simplicity reasons the app support only one date per user per activity type. (e.g., one physical activity per day)
2. The date format should be in the format YYYY-MM-DD
4. The API is designed with multiple updated in a day although it is not possible in the current design.



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
    """
    Calculate the weighted average of a pandas Series where later values have exponentially more weight.

    Parameters:
    series (pd.Series): The input series.
    base (float): The base of the exponential function. Default is 2.

    Returns:
    float: The exponentially weighted average.
    """
    # Generate exponential weights
    weights = np.arange(len(series))
    base = np.full_like(weights, base)
    np.power(base, weights, out=weights)

    # Calculate the weighted average
    weighted_avg = np.sum(series * weights) / np.sum(weights)

    return weighted_avg


@app.get('/get_health_score/{user_id}')
def get_health_score(user_id: int):
    """
    Get the health score of a user based on their physical, sleep and blood data.
    The health score itself is kind of nonsense, but it's a simple way to combine the three data types into one value,
    While giving more weight to more recent data.
    """
    user_data = user.get_user(user_id)
    age_range = get_age_range(user_data.age)
    physical_by_month = physical.get_avg_monthly(user_id)
    sleep_by_month = sleep.get_avg_monthly(user_id)
    blood_by_month = blood.get_avg_monthly(user_id)

    # getting weighted average of the physical, sleep and blood data so more recent data has more weight
    physicals = [exponential_weighted_average(activity) for activity in physical_by_month]
    sleeps = [exponential_weighted_average(data) for data in sleep_by_month]
    bloods = [exponential_weighted_average(count) for count in blood_by_month]

    physical_score = sum(physicals)
    sleep_score = sum(sleeps)
    blood_score = sum(bloods)
    calculated_score = (physical_score + sleep_score + blood_score) / 3

    all_avg_physical = physical.get_avg_all()
    all_avg_sleep = sleep.get_avg_all()
    all_avg_blood = blood.get_avg_all()

    physicals_all = [exponential_weighted_average(activity) for activity in all_avg_physical]
    sleeps_all = [exponential_weighted_average(data) for data in all_avg_sleep]
    bloods_all = [exponential_weighted_average(count) for count in all_avg_blood]

    physical_score_all = sum(physicals_all)
    sleep_score_all = sum(sleeps_all)
    blood_score_all = sum(bloods_all)
    calculated_score_all = (physical_score_all + sleep_score_all + blood_score_all) / 3

    final_score = 100 * (calculated_score / calculated_score_all)

    return {'health_score': final_score}


@app.get("/")
def root():
    return {"message": "Health Tracker API Root"}
