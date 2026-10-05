import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def register_test_user():
    login_id = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "Test@12345"
    response = client.post("/register", json={
        "login_id": login_id, "password": password,
        "emp_name": "Test User", "emp_age": 30,
        "emp_gender": "Male", "emp_branch": "QA",
    })
    assert response.status_code == 201
    return login_id, password

def test_login_success():
    login_id, password = register_test_user()
    response = client.post("/login", json={"login_id": login_id, "password": password})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

def test_login_wrong_password():
    login_id, _ = register_test_user()
    response = client.post("/login", json={"login_id": login_id, "password": "wrong_password"})
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Invalid credentials"
#
# def test_login_with_unregistered_login_id_returns_invalid_credentials():
#     # behaviour: An unregistered login_id is rejected with the same safe error response.
#     # arrange: Generate a login_id that cannot collide with any registered test user.
#     login_id = f"unregistered_{uuid.uuid4().hex}@example.com"
#     # act: Attempt to log in with the unregistered login_id.
#     response = client.post("/login", json={"login_id": login_id, "password": "Test@12345"})
#     # assert: The response is 401 and states that the credentials are invalid.
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Invalid credentials"

def test_unknown_user_gets_same_error_as_wrong_password():
    login_id, password = register_test_user()
    wrong_password = client.post("/login", json={"login_id": login_id, "password": "wrong_password"})
    unknown_user = client.post("/login", json={"login_id": f"nobody_{uuid.uuid4().hex[:8]}@example.com", "password": password})
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()
