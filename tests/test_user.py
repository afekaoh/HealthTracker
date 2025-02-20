from tests.test_setup import client, create_test_user, setup_and_teardown

a = setup_and_teardown


def test_create_user_successfully():
    response = client.post('/users/', json={'user_name': 'john_doe', 'name': 'John Doe', 'age': 30})
    assert response.status_code == 200
    assert response.json()['message'] == 'User John Doe created successfully'


def test_get_existing_user_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.get(f'/users/{user.user_name}')
    assert response.status_code == 200
    assert response.json() == {'user_name': user.user_name, 'name': user.name, 'age': user.age}


def test_get_nonexistent_user_returns_404():
    response = client.get('/users/nonexistent_user')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_update_user_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.put(f'/users/{user.user_name}', json={'user_name': 'john_doe', 'name': 'Jane Smith', 'age': 26})
    assert response.status_code == 200
    assert response.json()['message'] == 'User Jane Smith updated successfully'


def test_delete_user_successfully():
    user = create_test_user('john_doe', 'Jane Doe', 25)
    response = client.delete(f'/users/{user.user_name}')
    assert response.status_code == 200
    assert response.json()['message'] == f'User {user.name} was deleted successfully with all related data'


def test_delete_nonexistent_user_returns_404():
    response = client.delete('/users/nonexistent_user')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_create_user_with_invalid_age_returns_422():
    response = client.post('/users/', json={'user_name': 'john_doe', 'name': 'John Doe', 'age': 17})
    assert response.status_code == 422


def test_create_user_with_missing_fields_returns_422():
    response = client.post('/users/', json={'user_name': 'john_doe'})
    assert response.status_code == 422


def test_get_user_with_invalid_user_name_returns_404():
    response = client.get('/users/invalid_user')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_update_user_with_invalid_user_name_returns_404():
    create_test_user('asd', 'Jane Doe', 25)
    response = client.put('/users/invalid_user', json={'user_name': 'john_doe', 'name': 'Jane Smith', 'age': 26})
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_delete_user_with_invalid_user_name_returns_404():
    create_test_user('john_doe', 'Jane Doe', 25)
    response = client.delete('/users/invalid_user')
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_create_user_with_duplicate_user_name_returns_400():
    create_test_user('john_doe', 'John Doe', 30)
    response = client.post('/users/', json={'user_name': 'john_doe', 'name': 'John Doe', 'age': 30})
    assert response.status_code == 400
    assert response.json()['detail'] == 'User with this user_name already exists'

def test_update_user_with_duplicate_user_name_returns_400():
    # the catch here is that becuase we have no authentication, we can't update the user_name
    create_test_user('john_doe', 'John Doe', 30)
    user = create_test_user('jane_doe', 'Jane Doe', 25)
    response = client.put(f'/users/{user.user_name}', json={'user_name': 'john_doe', 'name': 'Jane Smith', 'age': 26})
    assert response.status_code == 200
    assert response.json()['message'] == 'User Jane Smith updated successfully'

