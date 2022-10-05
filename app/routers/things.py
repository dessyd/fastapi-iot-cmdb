from ast import In
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(
  prefix="/things",
  tags=["Things"]
)

@router.get("/", response_model=List[schemas.ThingOut])
async def get_all_things(db: Session = Depends(get_db)):
    things = db.query(models.Thing).all()
    return things

@router.post("/", response_model=schemas.ThingOut, status_code=status.HTTP_201_CREATED)
def create_one_thing(thing: schemas.ThingCreate, db: Session = Depends(get_db)):

  new_thing = models.Thing(**thing.dict())

  db.add(new_thing)
  db.commit()

  db.refresh(new_thing)

  return new_thing
