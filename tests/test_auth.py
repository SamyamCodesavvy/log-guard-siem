from tests.conftest import client


def test_register_user(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.json()
    assert data['username'] == 'testuser'
    assert 'hashed_password' not in data


# NEVER expose password hash
def test_login_success(client):
    client.post('/auth/register', json={
        'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'
        })
    response = client.post('/auth/login', json={
        'username': 'testuser', 'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()

def test_login_wrong_password(client):
    client.post('/auth/register', json={
        'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'
    })
    response = client.post('/auth/login', json={
        'username': 'testuser', 'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_protected_route_without_token(client):
    response = client.get('/hosts/')
    assert response.status_code == 403