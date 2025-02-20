from Backend.routers.blood import get_avg_all, get_avg_monthly
from tests.test_setup import client, create_test_user, override_get_db, setup_and_teardown

a = setup_and_teardown


def test_create_blood_test_successfully():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Created Blood test to user {user.name} on 2023-10-01'


def test_get_blood_tests_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.get(f'/blood/{user.user_name}')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 1


def test_get_blood_tests_with_filter_last():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.get(f'/blood/{user.user_name}?filter_last=true')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 1


def test_get_blood_tests_with_filter_by_date():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.get(f'/blood/{user.user_name}?filter_by_date=2023-10-01')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 1


def test_update_blood_test_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.put(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 5.0,
        'WBC'                : 7.0,
        'glucose_level'      : 95,
        'cholesterol_level'  : 185,
        'triglycerides_level': 155,
        'test_date'          : '2023-10-01'
    })
    assert response.status_code == 200
    assert response.json()['message'] == f'Updated Blood test for user {user.name} on 2023-10-01'


def test_delete_blood_test_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.delete(f'/blood/{user.user_name}?delete_all=true')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Blood tests for user {user.name}'


def test_delete_blood_test_with_dates():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    response = client.delete(f'/blood/{user.user_name}?delete_dates=2023-10-01')
    assert response.status_code == 200
    assert response.json()['message'] == f'Deleted Blood tests for user {user.name}'


def test_get_avg_monthly_successfully():
    db = next(override_get_db())

    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.8,
        'WBC'                : 6.2,
        'glucose_level'      : 92,
        'cholesterol_level'  : 182,
        'triglycerides_level': 152,
        'test_date'          : '2023-10-02'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.9,
        'WBC'                : 6.3,
        'glucose_level'      : 93,
        'cholesterol_level'  : 183,
        'triglycerides_level': 153,
        'test_date'          : '2023-10-03'
    })
    RBC, WBC, glucose_level, cholesterol_level, triglycerides_level = get_avg_monthly(user.user_name, db)
    assert len(RBC) > 0
    assert len(WBC) > 0
    assert len(glucose_level) > 0
    assert len(cholesterol_level) > 0
    assert len(triglycerides_level) > 0


def test_get_avg_all_successfully():
    db = next(override_get_db())
    user = create_test_user('john_doe', 'Jane Doe', 25)
    user1 = create_test_user('john_doe1', 'Jane Doe', 27)
    user2 = create_test_user('john_doe2', 'Jane Doe', 28)
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.5,
        'WBC'                : 6.0,
        'glucose_level'      : 90,
        'cholesterol_level'  : 180,
        'triglycerides_level': 150,
        'test_date'          : '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user1.user_name,
        'RBC'                : 4.6,
        'WBC'                : 6.1,
        'glucose_level'      : 91,
        'cholesterol_level'  : 181,
        'triglycerides_level': 151,
        'test_date'          : '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user2.user_name,
        'RBC'                : 4.7,
        'WBC'                : 6.2,
        'glucose_level'      : 92,
        'cholesterol_level'  : 182,
        'triglycerides_level': 152,
        'test_date'          : '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 4.8,
        'WBC'                : 6.3,
        'glucose_level'      : 93,
        'cholesterol_level'  : 183,
        'triglycerides_level': 153,
        'test_date'          : '2023-10-02'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user1.user_name,
        'RBC'                : 4.9,
        'WBC'                : 6.4,
        'glucose_level'      : 94,
        'cholesterol_level'  : 184,
        'triglycerides_level': 154,
        'test_date'          : '2023-10-02'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name'          : user2.user_name,
        'RBC'                : 5.0,
        'WBC'                : 6.5,
        'glucose_level'      : 95,
        'cholesterol_level'  : 185,
        'triglycerides_level': 155,
        'test_date'          : '2023-10-02'
    })
    RBC, WBC, glucose_level, cholesterol_level, triglycerides_level = get_avg_all(range(25, 30), db)
    assert len(RBC) > 0
    assert len(WBC) > 0
    assert len(glucose_level) > 0
    assert len(cholesterol_level) > 0
    assert len(triglycerides_level) > 0

    def test_create_blood_test_with_existing_date_returns_400():
        user = create_test_user('john_doe', 'John Doe', 30)
        client.post(f'/blood/{user.user_name}', json={
            'user_name'          : user.user_name,
            'RBC'                : 4.5,
            'WBC'                : 6.0,
            'glucose_level'      : 90,
            'cholesterol_level'  : 180,
            'triglycerides_level': 150,
            'test_date'          : '2023-10-01'
        })
        response = client.post(f'/blood/{user.user_name}', json={
            'user_name'          : user.user_name,
            'RBC'                : 4.8,
            'WBC'                : 6.2,
            'glucose_level'      : 92,
            'cholesterol_level'  : 182,
            'triglycerides_level': 152,
            'test_date'          : '2023-10-01'
        })
        assert response.status_code == 400
        assert response.json()['detail'] == 'Blood test already exists for this date, use PUT to update it'


def test_get_blood_tests_with_both_filters_returns_400():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/blood/{user.user_name}?filter_by_date=2023-10-01&filter_last=true')
    assert response.status_code == 400
    assert response.json()['detail'] == 'Only one filter can be applied at a time'


def test_get_blood_tests_with_no_data_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/blood/{user.user_name}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'No Blood test found for this user'


def test_update_blood_test_with_no_data_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.put(f'/blood/{user.user_name}', json={
        'user_name'          : user.user_name,
        'RBC'                : 5.0,
        'WBC'                : 7.0,
        'glucose_level'      : 95,
        'cholesterol_level'  : 185,
        'triglycerides_level': 155,
        'test_date'          : '2023-10-01'
    })
    assert response.status_code == 404
    assert response.json()['detail'] == 'No blood test found for this date'


def test_delete_blood_test_with_no_data_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.delete(f'/blood/{user.user_name}?delete_dates=2023-10-01')
    assert response.status_code == 404
    assert response.json()['detail'] == 'No blood test found to delete'


def test_delete_blood_test_with_no_params_returns_400():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.delete(f'/blood/{user.user_name}')
    assert response.status_code == 400
    assert response.json()['detail'] == 'No delete parameters provided'


def test_create_blood_test_with_missing_fields_returns_422():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180
    })
    assert response.status_code == 422

def test_create_blood_test_with_invalid_values_returns_422():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': -4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-10-01'
    })
    assert response.status_code == 422

def test_update_blood_test_with_invalid_values_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-10-01'
    })
    response = client.put(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': -5.0,
        'WBC': 7.0,
        'glucose_level': 95,
        'cholesterol_level': 185,
        'triglycerides_level': 155,
        'test_date': '2023-10-01'
    })
    assert response.status_code == 422

def test_update_blood_test_with_missing_fields_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-10-01'
    })
    response = client.put(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 5.0,
        'WBC': 7.0,
        'glucose_level': 95,
        'cholesterol_level': 185
    })
    assert response.status_code == 422

def test_create_blood_test_with_invalid_date_format_returns_422():
    user = create_test_user('john_doe', 'John Doe', 30)
    response = client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-13-01'
    })
    assert response.status_code == 422

def test_update_blood_test_with_invalid_date_format_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-10-01'
    })
    response = client.put(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 5.0,
        'WBC': 7.0,
        'glucose_level': 95,
        'cholesterol_level': 185,
        'triglycerides_level': 155,
        'test_date': '2023-13-01'
    })
    assert response.status_code == 422
    
def test_get_blood_tests_with_multiple_entries():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.8,
        'WBC': 6.2,
        'glucose_level': 92,
        'cholesterol_level': 182,
        'triglycerides_level': 152,
        'test_date': '2023-10-02'
    })
    response = client.get(f'/blood/{user.user_name}')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 2

def test_get_blood_tests_with_invalid_user_returns_404():
    response = client.get('/blood/invalid_user')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'

def test_get_blood_tests_with_invalid_date_format_returns_422():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/blood/{user.user_name}?filter_by_date=2023-13-01')
    assert response.status_code == 422

def test_get_blood_tests_with_nonexistent_date_returns_404():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/blood/{user.user_name}?filter_by_date=2023-10-01')
    assert response.status_code == 404
    assert response.json()['detail'] == 'No Blood test found for this user on the provided dates'

def test_get_blood_tests_with_multiple_dates():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.8,
        'WBC': 6.2,
        'glucose_level': 92,
        'cholesterol_level': 182,
        'triglycerides_level': 152,
        'test_date': '2023-10-02'
    })
    response = client.get(f'/blood/{user.user_name}?filter_by_date=2023-10-01&filter_by_date=2023-10-02')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 2

def test_get_blood_tests_with_filter_last_multiple_entries():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.5,
        'WBC': 6.0,
        'glucose_level': 90,
        'cholesterol_level': 180,
        'triglycerides_level': 150,
        'test_date': '2023-10-01'
    })
    client.post(f'/blood/{user.user_name}', json={
        'user_name': user.user_name,
        'RBC': 4.8,
        'WBC': 6.2,
        'glucose_level': 92,
        'cholesterol_level': 182,
        'triglycerides_level': 152,
        'test_date': '2023-10-02'
    })
    response = client.get(f'/blood/{user.user_name}?filter_last=true')
    assert response.status_code == 200
    assert response.json()['user'] == user.name
    assert len(response.json()['blood_tests']) == 1
    assert response.json()['blood_tests'][0]['RBC'] == 4.8