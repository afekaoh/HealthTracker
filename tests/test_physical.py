from Backend.routers.physical import get_avg_all, get_avg_monthly
from tests.test_setup import client, create_test_user, override_get_db, setup_and_teardown

a = setup_and_teardown


def test_create_physical_successfully():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Created Physical data to user {user.name} on 2023-10-01'


def test_get_physical_data_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.get(f'/physical/{user.user_name}')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 1


def test_get_physical_data_with_filter_last():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.get(f'/physical/{user.user_name}?filter_last=true')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 1


def test_get_physical_data_with_filter_by_date():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.get(f'/physical/{user.user_name}?filter_by_date=2023-10-01')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 1


def test_update_physical_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.put(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1500,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Updated Physical data for user {user.name} on 2023-10-01'


def test_delete_physical_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.delete(f'/physical/{user.user_name}?delete_all=true')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Physical data for user {user.name}'


def test_delete_physical_with_dates():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.delete(f'/physical/{user.user_name}?delete_dates=2023-10-01')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Physical data for user {user.name}'


def test_get_avg_monthly_successfully():
    db = next(override_get_db())
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 2000,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-02'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 3000,
        'cardio_time_session_minutes'  : 50,
        'strength_time_session_minutes': 40,
        'session_date'                 : '2023-10-03'
    })
    steps, cardio, strength = get_avg_monthly(user.user_name, db)
    assert len(steps) > 0
    assert len(cardio) > 0
    assert len(strength) > 0


def test_get_avg_all_successfully():
    db = next(override_get_db())
    user = create_test_user('john_doe', 'Jane Doe', 25)
    user1 = create_test_user('john_doe1', 'Jane Doe', 27)
    user2 = create_test_user('john_doe2', 'Jane Doe', 28)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user1.user_name,
        'steps'                        : 2000,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-01'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user2.user_name,
        'steps'                        : 3000,
        'cardio_time_session_minutes'  : 50,
        'strength_time_session_minutes': 40,
        'session_date'                 : '2023-10-01'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-02'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user1.user_name,
        'steps'                        : 2000,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-02'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user2.user_name,
        'steps'                        : 3000,
        'cardio_time_session_minutes'  : 50,
        'strength_time_session_minutes': 40,
        'session_date'                 : '2023-10-02'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-03'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user1.user_name,
        'steps'                        : 2000,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-03'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user2.user_name,
        'steps'                        : 3000,
        'cardio_time_session_minutes'  : 50,
        'strength_time_session_minutes': 40,
        'session_date'                 : '2023-10-03'
    })

    steps, cardio, strength = get_avg_all(range(25, 30), db)
    assert len(steps) > 0
    assert len(cardio) > 0
    assert len(strength) > 0


def test_create_physical_with_existing_date_returns_400():
    user = create_test_user('john_doe', 'John Doe', 30)
    client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1000,
        'cardio_time_session_minutes'  : 30,
        'strength_time_session_minutes': 20,
        'session_date'                 : '2023-10-01'
    })
    response = client.post(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1500,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-01'
    })
    assert response.status_code == 400
    assert response.json()['detail'] == 'Physical data already exists for this date, use PUT to update it'


def test_get_physical_data_with_both_filters_returns_400():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/physical/{user.user_name}?filter_by_date=2023-10-01&filter_last=true')
    assert response.status_code == 400
    assert response.json()['detail'] == 'Only one filter can be applied at a time'


def test_get_physical_data_with_no_data_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/physical/{user.user_name}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'No physical data found for this user'


def test_update_physical_with_no_data_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.put(f'/physical/{user.user_name}', json={
        'user_name'                    : user.user_name,
        'steps'                        : 1500,
        'cardio_time_session_minutes'  : 40,
        'strength_time_session_minutes': 30,
        'session_date'                 : '2023-10-01'
    })
    assert response.status_code == 404
    assert response.json()['detail'] == 'No physical data found for this date'


def test_delete_physical_with_no_data_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.delete(f'/physical/{user.user_name}?delete_dates=2023-10-01')
    assert response.status_code == 404
    assert response.json()['detail'] == 'No physical data found for the provided dates'


def test_delete_physical_with_no_params_returns_400():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.delete(f'/physical/{user.user_name}')
    assert response.status_code == 400
    assert response.json()['detail'] == 'No delete parameters provided'

def test_create_physical_with_missing_fields_returns_422():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000
    })
    assert response.status_code == 422

def test_create_physical_with_invalid_values_returns_422():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': -1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-10-01'
    })
    assert response.status_code == 422

def test_update_physical_with_invalid_values_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-10-01'
    })
    response = client.put(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': -1500,
        'cardio_time_session_minutes': 40,
        'strength_time_session_minutes': 30,
        'session_date': '2023-10-01'
    })
    assert response.status_code == 422

def test_update_physical_with_missing_fields_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-10-01'
    })
    response = client.put(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1500,
        'cardio_time_session_minutes': 40
    })
    assert response.status_code == 422

def test_create_physical_with_invalid_date_format_returns_422():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-13-01'
    })
    assert response.status_code == 422

def test_update_physical_with_invalid_date_format_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-10-01'
    })
    response = client.put(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1500,
        'cardio_time_session_minutes': 40,
        'strength_time_session_minutes': 30,
        'session_date': '2023-13-01'
    })
    assert response.status_code == 422
    
def test_get_physical_data_with_multiple_entries():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-10-01'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 2000,
        'cardio_time_session_minutes': 40,
        'strength_time_session_minutes': 30,
        'session_date': '2023-10-02'
    })
    response = client.get(f'/physical/{user.user_name}')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 2

def test_get_physical_data_with_invalid_user_returns_404():
    response = client.get('/physical/invalid_user')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'

def test_get_physical_data_with_invalid_date_format_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/physical/{user.user_name}?filter_by_date=2023-13-01')
    assert response.status_code == 422

def test_get_physical_data_with_nonexistent_date_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/physical/{user.user_name}?filter_by_date=2023-10-01')
    assert response.status_code == 404
    assert response.json()['detail'] == 'No physical data found for this user on the provided dates'

def test_get_physical_data_with_multiple_dates():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-10-01'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 2000,
        'cardio_time_session_minutes': 40,
        'strength_time_session_minutes': 30,
        'session_date': '2023-10-02'
    })
    response = client.get(f'/physical/{user.user_name}?filter_by_date=2023-10-01&filter_by_date=2023-10-02')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 2

def test_get_physical_data_with_filter_last_multiple_entries():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 1000,
        'cardio_time_session_minutes': 30,
        'strength_time_session_minutes': 20,
        'session_date': '2023-10-01'
    })
    client.post(f'/physical/{user.user_name}', json={
        'user_name': user.user_name,
        'steps': 2000,
        'cardio_time_session_minutes': 40,
        'strength_time_session_minutes': 30,
        'session_date': '2023-10-02'
    })
    response = client.get(f'/physical/{user.user_name}?filter_last=true')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['physical_data']) == 1
    assert response.json()['physical_data'][0]['steps'] == 2000