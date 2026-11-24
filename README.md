# Users CRUD — Python `http.server` example

A small CRUD app (create / read / update / delete users) built with the Python
standard library's `http.server`, MySQL, and Jinja2 templates. No Flask, no
FastAPI — the HTTP plumbing is intentionally visible.

## What you need

- Python 3.13
- MySQL (running locally by default)
- `pip`

## Setup

```bash
# 1. create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 2. install dependencies
pip install -r requirements.txt

# 3. create your local config (copy the sample, then edit it)
cp .env.sample .env

# 4. create the database and table
```

```sql
CREATE DATABASE youtuber;
USE youtuber;

CREATE TABLE users (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age  INT NOT NULL
);
```

Match the `DB_*` values in `.env` to your MySQL user/password.

## Run

```bash
python main.py
```

Then open <http://localhost:3000>.

## Routes

| Method | Path                      | Action            |
|--------|---------------------------|-------------------|
| GET    | `/`                       | list users        |
| GET    | `/users/new`              | new-user form     |
| POST   | `/users`                  | create user       |
| GET    | `/users/<id>/edit`        | edit-user form    |
| POST   | `/users/<id>/update`      | update user       |
| POST   | `/users/<id>/delete`      | delete user       |

## Project layout

```
main.py                       wires everything together, starts the server
config/
  setting.py                  reads .env into settings
  connection.py               Database class — hides the MySQL pool
handlers/
  user_handler.py             HTTP layer: parse request, render template
services/
  user_service.py             validation and business rules
repositories/
  user_repository.py          SQL; gets a connection per operation
models/
  user_model.py               User / UserInput dataclasses
routes/
  user_routes.py              URL patterns → handler method names
templates/
  index.html                  user list (contains the {% for %} loop)
  form.html                   create / edit form
  _error.html                 shared error alert
  error.html                  404 / 500 page
.env.sample                   config template (safe to commit)
requirements.txt              pinned dependencies
```

## Request flow

```
GET /  →  do_GET()  →  dispatch()  →  resolve()  →  index()
       →  UserService.find_all()  →  UserRepository.find_all()
       →  Database.connect()  →  cursor / SQL  →  Jinja renders index.html
```

Each layer only knows the one below it. The handler never writes SQL, and the
repository never writes HTML.

## Notes

**What is `.venv`?** A *virtual environment* — a private copy of Python plus
the packages this project needs, stored in a local folder. It keeps this
project's dependencies from mixing with other projects on your machine. You
activate it before running or installing anything. It is generated, large, and
machine-specific, so it must **not** be committed (see `.gitignore`).

**Why `do_GET` / `do_POST`?** `BaseHTTPRequestHandler` finds handlers by name:
on a GET it calls `getattr(self, "do_GET")()`. That's why there's no visible
call site — the stdlib calls them. Both simply forward to `dispatch()` so the
routing logic lives in one place.

**Connections vs. the pool.** `Database` owns the `MySQLConnectionPool`. Code
outside `config/` only ever sees a connection, via
`with database.connect() as connection:`. A pooled connection's `close()`
returns it to the pool, so you must get a fresh one for every operation —
caching one in `__init__` breaks after the first request.
