# Employee Management API

A small REST API built with **FastAPI** and **PostgreSQL**. Users can register as employees, log in to get a JWT access token, see who they are logged in as, and reach an admin-only route.

I built it as a backend practice project to learn authentication, password hashing, request validation, database constraints and role-based access control (RBAC).

## Tech stack

| Part | Tool | Version |
|---|---|---|
| Web framework | FastAPI | 0.141.1 |
| Server | Uvicorn | 0.53.0 |
| Database | PostgreSQL, via psycopg | 3.3.5 |
| Request validation | Pydantic (installed with FastAPI, not pinned) | — |
| Password hashing | passlib + bcrypt | 1.7.4 / 4.0.1 |
| Tokens | PyJWT | 2.13.0 |
| Settings | python-dotenv | 1.2.3 |
| Tests | pytest + httpx | 9.1.1 / 0.28.1 |

Developed on Python 3.13 (needs Python 3.10 or newer).

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/AnshGIll/employee-management-api.git
cd employee-management-api
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

**3. Install the dependencies**
```bash
pip install -r requirements.txt
```

**4. Create the database and its tables**
```bash
createdb -U postgres employee_db
psql -U postgres -d employee_db -f schema.sql
```

**5. Create a `.env` file** in the project folder (see [Environment variables](#environment-variables)). It is listed in `.gitignore` and must never be committed.

**6. Start the API**
```bash
uvicorn main:app --reload
```
The interactive docs open at http://127.0.0.1:8000/docs.

> **Windows note:** if Windows Smart App Control blocks psycopg's binary driver, add PostgreSQL's `bin` folder (for example `C:\Program Files\PostgreSQL\18\bin`) to your `PATH`.

## Environment variables

The app reads six values from `.env`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=employee_db
DB_USER=postgres
DB_PASSWORD=<your database password>
JWT_SECRET=<a long random secret>
```

Make a strong `JWT_SECRET` with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
`database.py` reads the five `DB_` values. `auth.py` reads `JWT_SECRET` and stops at startup if it is missing.

## Endpoints

| Method | Path | Who can call it | Success | Errors |
|---|---|---|---|---|
| POST | `/register` | anyone | `201` `{"message": "User registered successfully"}` | `409` login ID already taken · `422` invalid input |
| POST | `/login` | anyone | `200` `{"access_token": "...", "token_type": "bearer"}` | `401` `Invalid credentials` · `422` invalid input |
| GET | `/me` | any logged-in user | `200` `{"user_id": 7, "role": "employee"}` | `401` missing or bad token |
| GET | `/admin/ping` | admins only | `200` `{"message": "admin ok", "user_id": 1}` | `401` missing or bad token · `403` `Insufficient permissions` |

**Sending the token:** put it in the `Authorization` header as `Bearer <token>`. The word `Bearer` is accepted in any letter case. Tokens expire after 30 minutes.

```bash
curl http://127.0.0.1:8000/me -H "Authorization: Bearer <token>"
```
(In Windows PowerShell, type `curl.exe` instead of `curl`.)

**`/register` input rules** (a broken rule gives `422` before any database work):

| Field | Rule |
|---|---|
| `login_id` | 1–100 characters |
| `password` | 8–72 characters (72 bytes is the most bcrypt uses) |
| `emp_name` | 1–30 characters |
| `emp_age` | 18 to 60 |
| `emp_gender` | exactly `Male` or `Female` |
| `emp_branch` | 1–30 characters |

## Design decisions

- **Same answer for an unknown user and a wrong password.** Both return `401 Invalid credentials`, so nobody can use `/login` to find out which login IDs exist.
- **Passwords are stored only as bcrypt hashes.** Hashing (in `/register`) and checking (in `/login`) happen outside the database block. bcrypt is slow on purpose; doing it inside would hold a database connection idle, and connections are limited.
- **The token carries the user ID and role.** `/me` and `/admin/ping` read them from the token, with no database lookup. This is safe because the token is signed with `JWT_SECRET`: if anyone edits the role, the signature no longer matches and the request gets `401`.
- **401 vs 403.** `401` means "we don't know who you are" (missing, broken, tampered or expired token). `403` means "we know who you are, but your role isn't allowed here".
- **Two layers of checks.** Pydantic rejects bad input with `422` before any database code runs. The database then enforces its own rules as a second line of defence: `UNIQUE` on `users.login_id`, `UNIQUE` on `employee.user_id`, and a `CHECK` that `user_role` is `employee` or `admin`.
- **All-or-nothing database work.** Every request uses the `DBConnection` context manager: it commits if everything succeeds, rolls back if anything fails, and always closes the connection. So `/register` never leaves a user without an employee row.

## Known limitations

- **Login timing.** For an unknown login ID, bcrypt never runs, so the reply comes back slightly faster. A careful attacker could use that to guess which IDs exist.
- **Different 401 messages on protected routes.** `/me` and `/admin/ping` say *why* a token was rejected (`Not authenticated`, `Invalid authorization header format`, `Invalid token`, `Invalid token payload`, `Invalid user ID in token`). Helpful for debugging, but more than a client strictly needs to know.
- **No way to create an admin through the API.** `/register` always creates an `employee`. To make an admin, update the database directly:
  `UPDATE users SET user_role = 'admin' WHERE login_id = '<login id>';`
- **Tokens can't be revoked.** There is no logout; a token stays valid until it expires (30 minutes).
- **Gender is limited to `Male` and `Female`.**
- **Swagger's "Authorize" button isn't set up.** Typing a token into `/docs` doesn't send it, so use `curl` or the tests for protected routes.
- **Tests use the real database** and leave test users behind each run.
- **`database.py` doesn't check its settings at startup.** A missing `DB_` value only shows up later, as a connection error.

## Running the tests

The database must be running and `.env` must be set. Then:
```bash
python -m pytest
```

18 tests:

| File | Tests | What they check |
|---|---|---|
| `test_auth.py` | 3 | token holds the user ID and role · expires in about 30 minutes · a wrong secret is rejected |
| `test_login.py` | 3 | login works · wrong password gives `401` · unknown user gets the same error as a wrong password |
| `test_me.py` | 5 | valid token · no header · bad token · expired token · lowercase `bearer` |
| `test_rbac.py` | 3 | employee token gets `403` · no header gets `401` · admin token gets `200` |
| `test_validation.py` | 4 | age `0`, gender `"21"`, empty name, short password each give `422` |

## Project structure

| File | What it does |
|---|---|
| `main.py` | the four routes |
| `auth.py` | creating tokens, reading the current user from a token, the admin check |
| `hashing.py` | bcrypt hash and verify |
| `database.py` | the database connection and the `DBConnection` context manager |
| `schema.py` | Pydantic request and response models (the input rules above) |
| `schema.sql` | the `CREATE TABLE` statements for PostgreSQL |
| `test_*.py` | the test suite |
