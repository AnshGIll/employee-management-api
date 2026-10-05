from datetime import datetime, timezone
import jwt
import pytest

from auth import create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def test_token_contains_user_id_and_role():
    token = create_access_token(user_id = 7,role = "manager")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload['sub'] == "7"
    assert payload['role'] == "manager"

def test_token_exp():
    token = create_access_token(user_id=7, role="manager")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    now = datetime.now(timezone.utc).timestamp()
    seconds_left = payload["exp"] - now
    assert ACCESS_TOKEN_EXPIRE_MINUTES*60 -5 <= seconds_left <= ACCESS_TOKEN_EXPIRE_MINUTES*60

def test_token_wrong_secret():
    token = create_access_token(user_id=7, role="manager")
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "wrong_secret_123_4321_secrete_12", algorithms=[ALGORITHM])
