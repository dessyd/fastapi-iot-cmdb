from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import py_schemas, db_models, oauth2

router = APIRouter(
  prefix="/things",
  tags=["Things"]
)

