from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(
  prefix="/locations",
  tags=["Locations"]
)

@router.get("/", response_model=List(schemas.Location))
async def get_locations(db: Session = Depends(get_db)):
    locations = db.query(models.Location).all()
    return locations

@router.get("/{id}", response_model=schemas.LocationResponse)
async def get_location(id: int, db: Session = Depends(get_db)):

    location = db.query(models.Location).filter(models.Location.id == id).first()
    if  location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"Location with id {id} not found")
    return location

@router.post("/", status_code=status.HTTP_201_CREATED, 
              response_model=schemas.LocationResponse)
async def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):

    new_location = models.Location(**location.dict())
    print(new_location)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location