from test_login import client

valid = {
    "login_id": "validation_test@example.com",
    "password": "Test@12345",
    "emp_name": "Test User",
    "emp_age": 30,
    "emp_gender": "Male",
    "emp_branch": "QA",
}

def test_register_age_zero_returns_422():
    payload = {**valid, "emp_age": 0}
    response = client.post("/register", json=payload)
    # ASSERT: rejected by validation, and the error points at emp_age
    assert response.status_code == 422
    body = response.json()
    assert body["detail"][0]["loc"] == ["body", "emp_age"]

def test_register_gender_21_returns_422():
    payload = {**valid, "emp_gender": "21"}
    response = client.post("/register", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["detail"][0]["loc"] == ["body", "emp_gender"]

def test_register_empty_name_returns_422():
    payload = {**valid, "emp_name": ""}
    response = client.post("/register", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["detail"][0]["loc"] == ["body", "emp_name"]

def test_register_short_password_returns_422():
    payload = {**valid, "password": "Abc@123"}
    response = client.post("/register", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["detail"][0]["loc"] == ["body", "password"]