from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(locations.router)
app.include_router(things.router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/apple-touch-icon.png", include_in_schema=False)
async def apple_touch_icon():
    return FileResponse("static/apple-touch-icon.png")


@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
async def apple_touch_icon_precomposed():
    return FileResponse("static/apple-touch-icon-precomposed.png")


@app.get("/")
async def who_am_i():
    return {"message": "FastAPI-IoT-CMDB", "version": "1.1.0"}
