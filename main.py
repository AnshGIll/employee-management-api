from fastapi import(HTTPException, FastAPI, Depends)
from auth import(create_access_token, get_current_user, require_admin)
from database import DBConnection
from schema import RegisterRequest, LoginRequest, TokenResponse
from hashing import hash_password, verify_password
import psycopg
app=FastAPI()
@app.post("/register",status_code=201)
def register_user(request: RegisterRequest):
    hashed_password = hash_password(plain_password=request.password)
    try:
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (login_id, password_hash, user_role) "
                            "VALUES (%s,%s,%s) RETURNING user_id",
                            (request.login_id, hashed_password,"employee"))
            new_user = cursor.fetchone()
            user_id = new_user["user_id"]
            cursor.execute("INSERT INTO employee (user_id, emp_name, emp_age, emp_gender, branch) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            (user_id,request.emp_name,request.emp_age,request.emp_gender,request.emp_branch))
        return {"message": "User registered successfully"}
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="User already exists")

@app.post("/login",response_model=TokenResponse)
def login_user(request: LoginRequest):
    with DBConnection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, password_hash, user_role FROM users WHERE login_id = %s", (request.login_id, ))
        user = cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user["user_id"], user["user_role"]), "token_type": "bearer"}

@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/admin/ping")
def admin_ping(current_user: dict = Depends(require_admin)):
    return {"message": "admin ok", "user_id":current_user["user_id"]}