import logging

from fastapi import FastAPI

from Backend.routers import user, physical

logger = logging.getLogger(__name__)  # logging.getLogger('uvicorn.error').setLevel(logging.ERROR)
app = FastAPI(debug=True)

"""````````````````````````
I've decided not to implement any security measures for this API, as it is a simple example and to implement those correctly would be byond the scope and hide the true intention of this exmple.
In a real-world scenario, I would implement security measures such as authentication and authorization.
I'll also add in comments where would I add security measures.

1. There should be authentication for the users, so only the users can access their data. that should be done using a 3rd party service like OAuth2.
2. each endpoint should have authorization to check if the user has the right to access the data.
3. The data should be encrypted in the database.
4. The data should be encrypted during transit.
5. The API should have rate limiting.
"""

app.include_router(user.router)
app.include_router(physical.router)


# app.include_router(user.router)
# app.include_router(user.router)
# app.include_router(user.router)


# @app.post('/physical/')
# def add_new_activity(activity: UserPhysical):
#     id = activity.user_id
#     user = user_db.get(id, None)
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')
#     activity_to_db = {
#         'user_id'                      : id,
#         'id'                           : next(get_new_id()),
#         'steps'                        : activity.steps,
#         'cardio_time_session_minutes'  : activity.cardio_time_session_minutes,
#         'strength_time_session_minutes': activity.strength_time_session_minutes,
#         'session_date'                 : activity.session_date
#     }
#     physical_activity_db[activity_to_db['id']] = activity_to_db  # will be replaced with db insert
#     return {'message': f'Added Physical  to user {user}'}
#

# @app.post('/blood/')
# def add_new_blood_test(blood: UserBlood):
#     id = blood.user_id
#     user = user_db.get(id, None)
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')
#     blood_to_db = {
#         'user_id'            : id,
#         'id'                 : next(get_new_id()),
#         'RBC'                : blood.RBC,
#         'WBC'                : blood.WBC,
#         'glucose_level'      : blood.glucose_level,
#         'cholesterol_level'  : blood.cholesterol_level,
#         'triglycerides_level': blood.triglycerides_level,
#         'test_date'          : blood.test_date
#     }
#     blood_test_db[blood_to_db['id']] = blood_to_db  # will be replaced with db insert
#
#     return {'message': f'Added blood test to user {user["name"]}'}
#
#
# @app.post('/sleep/')
# def add_new_sleep(sleep: UserSleep):
#     id = sleep.user_id
#     user = user_db.get(id, None)
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')
#     sleep_to_db = {
#         'user_id'         : id,
#         'id'              : next(get_new_id()),
#         'sleep_hours'     : sleep.sleep_hours,
#         'avg_heart_rate'  : sleep.avg_heart_rate,
#         'avg_oxygen_level': sleep.avg_oxygen_level,
#         'sleep_date'      : sleep.sleep_date
#     }
#     sleep_activity_db[sleep_to_db['id']] = sleep_to_db  # will be replaced with db insert
#
#     return {'message': f'Added blood test to user {user["name"]}'}
#
#
#
# @app.get('/health/{user_id}')
# def get_health(user_id: int):
#     user = user_db.get(user_id, None)
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')
#     physical_activity = [v for k, v in physical_activity_db.items() if v['user_id'] == user_id]
#     sleep_activity = [v for k, v in sleep_activity_db.items() if v['user_id'] == user_id]
#     blood_test = [v for k, v in blood_test_db.items() if v['user_id'] == user_id]
#     return {
#         'user'             : user,
#         'physical_activity': physical_activity,
#         'sleep_activity'   : sleep_activity,
#         'blood_test'       : blood_test
#     }

@app.get('/get_health_score/{user_id}')
def get_health_score(user_id: int):
    # will have to wait for the other endpoints to be implemented
    return {'health_score': 100}


@app.get("/")
def root():
    return {"message": "Health Tracker API Root"}
