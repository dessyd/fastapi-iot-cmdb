from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/things",
    tags=["Things"],
    responses={404: {"description": "Thing not found"}},
)


@router.get("/", response_model=List[schemas.ThingOut])
async def get_all_things(db: Session = Depends(get_db)):
    things = db.query(models.Thing).all()
    return things


@router.get("/{id}", response_model=schemas.ThingOut)
async def get_one_thing(
    id: Annotated[int, Path(description="The ID of the thing to get")],
    db: Session = Depends(get_db),
):
    """
    Returns a specific thing identified by its id
    """
    thing = db.query(models.Thing).filter(models.Thing.id == id).first()
    if thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thing with id {id} not found",
        )
    return thing


@router.post("/", response_model=schemas.ThingOut, status_code=status.HTTP_201_CREATED)
async def create_one_thing(thing: schemas.ThingCreate, db: Session = Depends(get_db)):
    new_thing = models.Thing(**thing.model_dump())

    db.add(new_thing)
    db.commit()

    db.refresh(new_thing)

    return new_thing


@router.put("/{id}", response_model=schemas.ThingOut)
async def update_one_thing(
    id: Annotated[int, Path(description="The ID of the thing to update")],
    thing: schemas.ThingUpdate,
    db: Session = Depends(get_db),
):
    thing_query = db.query(models.Thing).filter(models.Thing.id == id)
    first_thing = thing_query.first()

    if first_thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"thing with id: {id} does not exist",
        )

    thing_query.update(jsonable_encoder(thing), synchronize_session=False)
    db.commit()

    return thing_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_thing(
    id: Annotated[int, Path(description="The ID of the thing to delete")],
    db: Session = Depends(get_db),
):
    """
    Delete a specific thing identified by its id
    """
    thing = db.query(models.Thing).filter(models.Thing.id == id)
    first_thing = thing.first()

    if first_thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thing with id: {id} does not exist",
        )

    thing.delete(synchronize_session=False)
    db.commit()

    return
