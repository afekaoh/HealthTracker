from tests.test_setup import client, create_test_user, setup_and_teardown

a = setup_and_teardown

import re


def test_get_health_score_successfully():
    user = create_test_user('john_doe', 'John Doe', 30)
    user1 = create_test_user('jane_doe', 'Jane Doe', 31)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    client.post(f'/sleep/{user.user_name}', json={
        'user_name'       : user.user_name,
        'sleep_hours'     : 8.0,
        'avg_heart_rate'  : 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date'      : '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    client.post(f'/physical/{user1.user_name}', json={
        'user_name'                    : user1.user_name,
        'steps'                        : 5000,
        'cardio_time_session_minutes'  : 60,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-01'
    })
    client.post(f'/sleep/{user1.user_name}', json={
        'user_name'       : user1.user_name,
        'sleep_hours'     : 7.0,
        'avg_heart_rate'  : 65.0,
        'avg_oxygen_level': 95.0,
        'sleep_date'      : '2023-10-01'
    })
    client.post(f'/blood/{user1.user_name}', json={
        'user_name'          : user1.user_name,
        'RBC'                : 5.5,
        'WBC'                : 7.0,
        'glucose_level'      : 100,
        'cholesterol_level'  : 190,
        'triglycerides_level': 160,
        'test_date'          : '2023-10-01'
    })
    response = client.get(f'/get_health_score/{user.user_name}')
    assert response.status_code == 200
    assert 'health_score' in response.json() and isinstance(response.json()['health_score'], float) and 0 < \
           response.json()['health_score']
    response = client.get(f'/get_health_score/{user1.user_name}')
    assert response.status_code == 200
    assert 'health_score' in response.json() and isinstance(response.json()['health_score'], float) and 0 < \
           response.json()['health_score']


def test_get_health_score_with_no_data_returns_404():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.get(f'/get_health_score/{user.user_name}')
    assert response.status_code == 404
    assert re.match(r'No \w+ (data|activity|tests) found for this user', response.json()['detail'])


def test_get_health_score_with_invalid_user_returns_404():
    response = client.get('/get_health_score/invalid_user')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_get_health_score_with_partial_data():
    user = create_test_user('john_doe', 'John Doe', 30)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    client.post(f'/sleep/{user.user_name}', json={
        'user_name'       : user.user_name,
        'sleep_hours'     : 8.0,
        'avg_heart_rate'  : 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date'      : '2023-10-01'
    })
    response = client.get(f'/get_health_score/{user.user_name}')
    assert response.status_code == 404
    assert re.match(r'No \w+ (data|activity|tests) found for this user', response.json()['detail'])
