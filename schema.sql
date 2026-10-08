CREATE TABLE users (
    user_id       SERIAL PRIMARY KEY,
    login_id      VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL,
    user_role     VARCHAR(10)  NOT NULL,
    CONSTRAINT users_user_role_check CHECK (user_role IN ('employee', 'admin'))
);

CREATE TABLE employee (
    employee_id     SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(user_id) NOT NULL,
    emp_name        VARCHAR(100) NOT NULL,
    emp_age         INTEGER NOT NULL,
    emp_gender      VARCHAR(10) NOT NULL,
    branch          VARCHAR(100),
    salary          NUMERIC(12,2),

    CONSTRAINT employee_user_id_key UNIQUE (user_id)
);