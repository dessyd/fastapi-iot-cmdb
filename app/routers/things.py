from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/things", tags=["Things"])


@router.get("/", response_model=List[schemas.ThingOut])
async def get_all_things(db: Session = Depends(get_db)):
    things = db.query(models.Thing).all()
    return things


@router.post("/", response_model=schemas.ThingOut, status_code=status.HTTP_201_CREATED)
def create_one_thing(thing: schemas.ThingCreate, db: Session = Depends(get_db)):
    new_thing = models.Thing(**thing.model_dump())

    db.add(new_thing)
    db.commit()

    db.refresh(new_thing)

    return new_thing
