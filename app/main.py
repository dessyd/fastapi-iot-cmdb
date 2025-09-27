from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI IoT CMDB",
        version="1.1.0",
        description="""
        **IoT Configuration Management Database (CMDB)** for tracking and managing IoT devices and their locations.

        This API provides comprehensive management capabilities for:

        * **Locations**: Physical sites where IoT devices are deployed
        * **Things**: IoT devices and equipment with MAC addresses and location associations

        The system maintains relationships between devices and their deployment locations,
        making it easy to track where equipment is installed and manage inventory across multiple sites.

        ## Features

        * Full CRUD operations for locations and things
        * Geographic coordinates support for locations
        * Foreign key relationships between things and locations
        * Automatic timestamp tracking for all entities
        * RESTful API design following OpenAPI standards
        """,
        routes=app.routes,
    )
    openapi_schema["tags"] = [
        {
            "name": "Locations",
            "description": "**Physical Location Management**\n\nManage physical locations where IoT devices are deployed. Each location includes geographic coordinates (latitude/longitude) for precise positioning, unique identifier and descriptive name, creation timestamp for audit tracking, and relationship management with associated things/devices.\n\nLocations serve as the primary organizational unit for device deployment, enabling geographic-based inventory management and site-specific operations.",
        },
        {
            "name": "Things",
            "description": "**IoT Device & Equipment Management**\n\nManage IoT devices and equipment tracked in the CMDB. Each thing includes MAC address for unique network identification, descriptive name and metadata, location association via foreign key relationship, and creation timestamp for audit tracking.\n\nThings represent the physical devices being monitored, providing complete device lifecycle management from deployment to decommissioning.",
        },
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI()
app.openapi = custom_openapi

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
