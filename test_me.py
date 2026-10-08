from datetime import datetime, timedelta, timezone   # tools to build an expired time
import jwt                                           # to hand-make a token for test 4
from auth import create_access_token, SECRET_KEY, ALGORITHM
from test_login import client     # reuse the fake browser already built in test_login.py


def test_me_valid_token_returns_user():
    # ARRANGE: make a real, valid token the same way /login does
    token = create_access_token(user_id=7, role="manager")

    # ACT: call /me, putting the token in the Authorization header
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    # ASSERT: request accepted, and the body is what get_current_user returns
    assert response.status_code == 200
    assert response.json() == {"user_id": 7, "role": "manager"}

def test_me_no_header_returns_401():
    response = client.get("/me")
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Not authenticated"

def test_me_bad_token_returns_401():
    response = client.get("/me", headers={"Authorization": "Bearer abc"})
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Invalid token"

def test_me_expired_token_returns_401():
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode({"sub": "7", "role": "manager", "exp": expired_time}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Invalid token"

def test_me_lowercase_bearer_token_returns_200():
    token = create_access_token(user_id=7, role="manager")
    response = client.get("/me", headers={"Authorization": f"bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"user_id": 7, "role": "manager"}