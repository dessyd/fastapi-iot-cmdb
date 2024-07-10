from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("/", response_model=List[schemas.LocationOut])
async def get_all_locations(db: Session = Depends(get_db)):
    locations = db.query(models.Location).all()
    return locations


@router.get("/{id}", response_model=schemas.LocationOut)
async def get_one_location(
    id: Annotated[int, Path(title="The ID of the location to get")], db: Session = Depends(get_db)
):
    location = db.query(models.Location).filter(models.Location.id == id).first()
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Location with id {id} not found"
        )
    return location


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.LocationOut)
async def create_one_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    new_location = models.Location(**location.model_dump())
    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_location(id: int, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(models.Location.id == id)
    first_location = location.first()

    if first_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Location with id: {id} does not exeist"
        )

    location.delete(synchronize_session=False)
    db.commit()

    return


@router.put("/{id}", response_model=schemas.LocationOut)
def update_one_location(id: int, location: schemas.LocationUpdate, db: Session = Depends(get_db)):
    location_query = db.query(models.Location).filter(models.Location.id == id)
    first_location = location_query.first()

    if first_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"location with id: {id} does not exist"
        )

    location_query.update(jsonable_encoder(location), synchronize_session=False)
    db.commit()

    return location_query.first()
