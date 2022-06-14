from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, users

# Needed if Alembic is not used to create / upgrade the structure
# models.Base.metadata.create_all(bind=engine)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)



@app.get("/")
def root():
    return {"message": "Hello Root"}