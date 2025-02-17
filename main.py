from Backend.main_api import app

user_data = [
    {
        'user'             :
            {
                "name": "John",
                "age" : 30
            },
        'physical_activity':
            {
                "steps"                        : 1000,
                "cardio_time_session_minutes"  : 30,
                "strength_time_session_minutes": 30,
                "session_date"                 : "2021-10-10"
            },
        'blood_test'       :
            {
                "RBC"                : 5.0,
                "WBC"                : 5.0,
                "glucose_level"      : 100,
                "cholesterol_level"  : 100,
                "triglycerides_level": 100,
                "test_date"          : "2021-10-10"
            },
        'sleep_activity'   :
            {
                "sleep_hours"     : 8,
                "avg_heart_rate"  : 60,
                "avg_oxygen_level": 90,
                "sleep_date"      : "2021-10-10"
            },
    },
    {
        'user2'            :
            {
                "name": "Alice",
                "age" : 25
            },
        'physical_activity':
            {
                "steps"                        : 2000,
                "cardio_time_session_minutes"  : 60,
                "strength_time_session_minutes": 60,
                "session_date"                 : "2021-10-11"
            },
        'blood_test'       :
            {
                "RBC"                : 4.5,
                "WBC"                : 4.5,
                "glucose_level"      : 90,
                "cholesterol_level"  : 90,
                "triglycerides_level": 90,
                "test_date"          : "2021-10-11"
            },
        'sleep_activity'   :
            {
                "sleep_hours"     : 7,
                "avg_heart_rate"  : 65,
                "avg_oxygen_level": 85,
                "sleep_date"      : "2021-10-11"
            },
    },
    {
        'user3'            :
            {
                "name": "Bob",
                "age" : 35
            },
        'physical_activity':
            {
                "steps"                        : 3000,
                "cardio_time_session_minutes"  : 90,
                "strength_time_session_minutes": 90,
                "session_date"                 : "2021-10-12"
            },
        'blood_test'       :
            {
                "RBC"                : 4.0,
                "WBC"                : 4.0,
                "glucose_level"      : 80,
                "cholesterol_level"  : 80,
                "triglycerides_level": 80,
                "test_date"          : "2021-10-12"
            },
        'sleep_activity'   :
            {
                "sleep_hours"     : 6,
                "avg_heart_rate"  : 70,
                "avg_oxygen_level": 80,
                "sleep_date"      : "2021-10-12"
            },
    }

]

# import requests
#
# for user in user_data:
#     user_data = user['user']
#     physical_activity = user['physical_activity']
#     blood_test = user['blood_test']
#     sleep_activity = user['sleep_activity']
#
#     response = requests.post('localhost:8888/users/', data=user_data)
#     print(response.json()['message'])
#     id = response.json()['id']
#     physical_activity['user_id'] = id
#     blood_test['user_id'] = id
#     sleep_activity['user_id'] = id
#     response = requests.post('localhost:8000/physical/', data=physical_activity)
#     print(response.json()['message'])
#     response = requests.post('localhost:8000/blood/', data=blood_test)
#     print(response.json()['message'])
#     response = requests.post('localhost:8000/sleep/', data=sleep_activity)
#     print(response.json()['message'])
#
#
