from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas, models

router = APIRouter(
  prefix="/locations",
  tags=["Locations"]
)

@router.get("/", response_model=List[models.LocationResponse])
async def get_locations(db: Session = Depends(get_db)):
    posts = db.query(schemas.Location).all()
    return posts

@router.get("/{id}", response_model=models.LocationResponse)
async def get_location(id: int, db: Session = Depends(get_db)):

    location = db.query(schemas.Location).filter(schemas.Location.id == id).first()
    if  location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"Location with id {id} not found")
    return location

@router.post("/", status_code=status.HTTP_201_CREATED, 
              response_model=models.LocationResponse)
async def create_location(location: models.Location, db: Session = Depends(get_db)):

    new_location = schemas.Location(**location.dict())
    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location