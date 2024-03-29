from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database

from .routers import locations, things

# Needed if Alembic is not used to create / upgrade the structure
# models.Base.metadata.create_all(bind=engine)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "https://localhost:8000",
]

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations.router)
app.include_router(things.router)


@app.get("/")
async def who_am_i():
    return {"message": "FastAPI-IoT-CMDB", "version": "1.1.0"}
