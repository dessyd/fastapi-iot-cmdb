from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Location, LocationCreate, LocationRead, LocationUpdate

router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
    responses={404: {"description": "Location not found"}},
)


@router.get("", response_model=List[LocationRead])
async def get_all_locations(session: Session = Depends(get_session)):
    """
    Returns all known locations
    """
    statement = select(Location)
    locations = session.exec(statement).all()
    return locations


@router.get("/{id}", response_model=LocationRead)
async def get_one_location(
    id: Annotated[int, Path(description="The ID of the location to get")],
    session: Session = Depends(get_session),
):
    """
    Returns a specific location identified by its id
    """
    statement = select(Location).where(Location.id == id)
    location = session.exec(statement).first()
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {id} not found",
        )
    return location


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=LocationRead,
)
async def create_one_location(location: LocationCreate, session: Session = Depends(get_session)):
    """
    Create a new location
    """
    db_location = Location.model_validate(location)
    session.add(db_location)
    session.commit()
    session.refresh(db_location)

    return db_location


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_location(
    id: Annotated[int, Path(description="The ID of the location to delete")],
    session: Session = Depends(get_session),
):
    statement = select(Location).where(Location.id == id)
    location = session.exec(statement).first()

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id: {id} does not exist",
        )

    session.delete(location)
    session.commit()

    return


@router.put("/{id}", response_model=LocationRead)
async def update_one_location(
    id: Annotated[int, Path(description="The ID of the location to update")],
    location: LocationUpdate,
    session: Session = Depends(get_session),
):
    statement = select(Location).where(Location.id == id)
    db_location = session.exec(statement).first()

    if db_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"location with id: {id} does not exist",
        )

    location_data = location.model_dump(exclude_unset=True)
    for key, value in location_data.items():
        setattr(db_location, key, value)

    session.add(db_location)
    session.commit()
    session.refresh(db_location)

    return db_location
