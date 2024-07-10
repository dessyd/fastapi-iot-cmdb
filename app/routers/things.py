from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
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


@router.put("/{id}", response_model=schemas.ThingOut)
def update_one_thing(
    id: Annotated[int, Path(title="The ID of the thing to get")],
    thing: schemas.ThingUpdate,
    db: Session = Depends(get_db),
):
    thing_query = db.query(models.Thing).filter(models.Thing.id == id)
    first_thing = thing_query.first()

    if first_thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"thing with id: {id} does not exist"
        )

    thing_query.update(jsonable_encoder(thing), synchronize_session=False)
    db.commit()

    return thing_query.first()
