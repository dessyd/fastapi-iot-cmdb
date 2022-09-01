# FastAPI IoT CMDB

## Details

### Local Setup

```bash
# Install Postgres
brew install postgresql
# Create virtual environment
python3 -m venv venv
# Activate it
source venv/bin/activate
# make sure pip is up to date
pip install --upgrade pip
# install project's requirements
pip install -r requirements.txt
# start database engine
docker compose up -d
# Initialize alembic file structure
alembic init alembic
# copy the project ini file
cp app/alembic.env.py alembic/env.py
# Autogenerate the database schema creation file
alembic revision --autogenerate -m "Application schema"
# Execute the schema creation
alembic upgrade head
# Start Web server:
uvicorn app.main:app --reload
```

## Modules dependencies

```mermaid
flowchart LR


 c(config)
 d(database)
 m(models)
 o(oauth2)
 ra(routers/auth)
 ru(routers/users)
 s(schemas)
 u(utils)

 d --> c
 m --> d
 o --> c
 o --> d
 o --> m
 o --> s

 main --> ra
 main --> ru

 ra --> d
 ra --> m
 ra --> o
 ra --> s
 ra --> u

 ru --> m
 ru --> s
 ru --> u
 ru --> d

```
