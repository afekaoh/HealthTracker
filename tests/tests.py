from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from Backend.DB import get_db, User
from Backend.main import app

client = TestClient(app)


def create_test_user(db: Session, name: str, age: int):
    user = User(name=name, age=age)
    db.add(user)
    db.commit()
    return user


# User tests

def create_user_successfully(db_session):
    response = client.post('/users/', json={'name': 'John Doe', 'age': 30})
    assert response.status_code == 200
    assert response.json()['message'] == 'User John Doe created successfully'


def get_existing_user(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    response = client.get(f'/users/{user.id}')
    assert response.status_code == 200
    assert response.json() == {'id': user.id, 'name': user.name, 'age': user.age}


def get_nonexistent_user(db_session):
    response = client.get('/users/999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def update_user_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    response = client.put(f'/users/{user.id}', json={'name': 'Jane Smith', 'age': 26})
    assert response.status_code == 200
    assert response.json()['message'] == 'User Jane Smith updated successfully'


def delete_user_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    response = client.delete(f'/users/{user.id}')
    assert response.status_code == 200
    assert response.json()['message'] == f'User {user.name} was deleted successfully with all related data'


def delete_nonexistent_user(db_session):
    response = client.delete('/users/999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


# Physical tests

def create_physical_successfully(db_session):
    user = create_test_user(db_session, 'John Doe', 30)
    response = client.post('/physical/', json={
        'user_id'                      : user.id,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Created Physical data to user {user.name} on 2023-10-01'


def get_physical_data_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/physical/', json={
        'user_id'                      : user.id,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.get(f'/physical/{user.id}')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 1


def get_physical_data_with_filter_last(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/physical/', json={
        'user_id'                      : user.id,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.get(f'/physical/{user.id}?filter_last=true')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 1


def get_physical_data_with_filter_by_date(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/physical/', json={
        'user_id'                      : user.id,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.get(f'/physical/{user.id}?filter_by_date=2023-10-01')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 1


def update_physical_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/physical/', json={
        'user_id'                      : user.id,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.put(f'/physical/{user.id}', json={
        'user_id'                      : user.id,
        'steps'                        : 1500,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Updated Physical data for user {user.name} on 2023-10-01'


def delete_physical_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/physical/', json={
        'user_id'                      : user.id,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.delete(f'/physical/{user.id}?delete_all=true')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Physical data for user {user.name}'


def delete_physical_with_dates(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/physical/', json={
        'user_id'                      : user.id,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.delete(f'/physical/{user.id}?delete_dates=2023-10-01')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Physical data for user {user.name}'


# Blood tests
def create_blood_test_successfully(db_session):
    user = create_test_user(db_session, 'John Doe', 30)
    response = client.post('/blood/', json={
        'user_id'            : user.id,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Created Blood test to user {user.name} on 2023-10-01'


def get_blood_tests_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/blood/', json={
        'user_id'            : user.id,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.get(f'/blood/{user.id}')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 1


def get_blood_tests_with_filter_last(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/blood/', json={
        'user_id'            : user.id,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.get(f'/blood/{user.id}?filter_last=true')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 1


def get_blood_tests_with_filter_by_date(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/blood/', json={
        'user_id'            : user.id,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.get(f'/blood/{user.id}?filter_by_date=2023-10-01')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 1


def update_blood_test_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/blood/', json={
        'user_id'            : user.id,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.put(f'/blood/{user.id}', json={
        'user_id'            : user.id,
        'RBC'                : 5.0,
        'WBC'                : 7.0,
        'glucose_level'      : 95,
        'cholesterol_level'  : 185,
        'triglycerides_level': 155,
        'test_date'          : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Updated Blood test for user {user.name} on 2023-10-01'


def delete_blood_test_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/blood/', json={
        'user_id'            : user.id,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.delete(f'/blood/{user.id}?delete_all=true')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Blood tests for user {user.name}'


def delete_blood_test_with_dates(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/blood/', json={
        'user_id'            : user.id,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.delete(f'/blood/{user.id}?delete_dates=2023-10-01')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Blood tests for user {user.name}'


# Sleep tests

def create_sleep_activity_successfully(db_session):
    user = create_test_user(db_session, 'John Doe', 30)
    response = client.post('/sleep/', json={
        'user_id': user.id,
        'sleep_hours': 8.0,
        'avg_heart_rate': 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date': '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Created Sleep activity to user {user.name} on 2023-10-01'

def get_sleep_activities_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/sleep/', json={
        'user_id': user.id,
        'sleep_hours': 8.0,
        'avg_heart_rate': 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date': '2023-10-01'
    })
    response = client.get(f'/sleep/{user.id}')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['sleep activity']) == 1

def get_sleep_activities_with_filter_last(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/sleep/', json={
        'user_id': user.id,
        'sleep_hours': 8.0,
        'avg_heart_rate': 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date': '2023-10-01'
    })
    response = client.get(f'/sleep/{user.id}?filter_last=true')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['sleep activity']) == 1

def get_sleep_activities_with_filter_by_date(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/sleep/', json={
        'user_id': user.id,
        'sleep_hours': 8.0,
        'avg_heart_rate': 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date': '2023-10-01'
    })
    response = client.get(f'/sleep/{user.id}?filter_by_date=2023-10-01')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['sleep activity']) == 1

def update_sleep_activity_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/sleep/', json={
        'user_id': user.id,
        'sleep_hours': 8.0,
        'avg_heart_rate': 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date': '2023-10-01'
    })
    response = client.put(f'/sleep/{user.id}', json={
        'user_id': user.id,
        'sleep_hours': 7.5,
        'avg_heart_rate': 62.0,
        'avg_oxygen_level': 97.0,
        'sleep_date': '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Updated sleep activity for user {user.name} on 2023-10-01'

def delete_sleep_activity_successfully(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/sleep/', json={
        'user_id': user.id,
        'sleep_hours': 8.0,
        'avg_heart_rate': 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date': '2023-10-01'
    })
    response = client.delete(f'/sleep/{user.id}?delete_all=true')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted sleep activity for user {user.name}'

def delete_sleep_activity_with_dates(db_session):
    user = create_test_user(db_session, 'Jane Doe', 25)
    client.post('/sleep/', json={
        'user_id': user.id,
        'sleep_hours': 8.0,
        'avg_heart_rate': 60.0,
        'avg_oxygen_level': 98.0,
        'sleep_date': '2023-10-01'
    })
    response = client.delete(f'/sleep/{user.id}?delete_dates=2023-10-01')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted sleep activity for user {user.name}'


user_tests = [
    create_user_successfully,
    get_existing_user,
    get_nonexistent_user,
    update_user_successfully,
    delete_user_successfully,
    delete_nonexistent_user
]

physical_tests = [
    create_physical_successfully,
    get_physical_data_successfully,
    get_physical_data_with_filter_last,
    get_physical_data_with_filter_by_date,
    update_physical_successfully,
    delete_physical_successfully,
    delete_physical_with_dates
]

blood_tests = [create_blood_test_successfully,
               get_blood_tests_successfully,
               get_blood_tests_with_filter_last,
               get_blood_tests_with_filter_by_date,
               update_blood_test_successfully,
               delete_blood_test_successfully,
               delete_blood_test_with_dates]

sleep_tests = [create_sleep_activity_successfully,
               get_sleep_activities_successfully,
               get_sleep_activities_with_filter_last,
               get_sleep_activities_with_filter_by_date,
               update_sleep_activity_successfully,
               delete_sleep_activity_successfully,
               delete_sleep_activity_with_dates]

if __name__ == '__main__':
    db_session = next(get_db())
    for test in user_tests:
        test(db_session)
    for test in physical_tests:
        test(db_session)
    for test in blood_tests:
        test(db_session)
    for test in sleep_tests:
        test(db_session)
