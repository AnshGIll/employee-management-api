from auth import create_access_token
from test_login import client

def test_admin_ping_employee_token_returns_403():
    token = create_access_token(user_id=1, role="employee")
    response = client.get("/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    body = response.json()
    assert body["detail"] == "Insufficient permissions"

def test_admin_ping_employee_no_header_returns_401():
    response = client.get("/admin/ping")
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Not authenticated"

def test_admin_ping_admin_token_returns_200():
    token = create_access_token(user_id=1, role="admin")
    response = client.get("/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body == {"message": "admin ok","user_id": 1}
