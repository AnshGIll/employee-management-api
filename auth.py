import os
from datetime import timedelta, datetime, timezone
import jwt
from dotenv import load_dotenv
from fastapi import Header, HTTPException, Depends

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
if SECRET_KEY is None:
    raise ValueError("JWT_SECRET environment variable is not set")

def create_access_token(user_id, role):
    to_encode = {"sub": str(user_id), "role": role}
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    sub = payload.get("sub")
    role = payload.get("role")
    if sub is None or role is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID in token")

    return {"user_id": user_id, "role": role}

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user
