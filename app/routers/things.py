from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..database import get_session
from ..models import Location, Thing, ThingCreate, ThingRead, ThingReadWithLocation, ThingUpdate

router = APIRouter(
    prefix="/things",
    tags=["Things"],
    responses={404: {"description": "Thing not found"}},
)


@router.get("/", response_model=List[ThingReadWithLocation])
async def get_all_things(session: Session = Depends(get_session)):
    """Get all things with their locations"""
    statement = select(Thing).join(Location)
    things = session.exec(statement).all()
    return things


@router.get("/{id}", response_model=ThingReadWithLocation)
async def get_one_thing(
    id: Annotated[int, Path(description="The ID of the thing to get")],
    session: Session = Depends(get_session),
):
    """
    Returns a specific thing identified by its id
    """
    statement = select(Thing).where(Thing.id == id)
    thing = session.exec(statement).first()
    if thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thing with id {id} not found",
        )
    return thing


@router.post("/", response_model=ThingRead, status_code=status.HTTP_201_CREATED)
async def create_one_thing(thing: ThingCreate, session: Session = Depends(get_session)):
    """Create a new thing"""
    try:
        # Validate location exists
        location_statement = select(Location).where(Location.id == thing.location_id)
        location = session.exec(location_statement).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Location not found"
            )

        db_thing = Thing.model_validate(thing)
        session.add(db_thing)
        session.commit()
        session.refresh(db_thing)

        return db_thing
    except IntegrityError as e:
        session.rollback()
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid location_id"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Database constraint violation"
        )


@router.put("/{id}", response_model=ThingRead)
async def update_one_thing(
    id: Annotated[int, Path(description="The ID of the thing to update")],
    thing: ThingUpdate,
    session: Session = Depends(get_session),
):
    """Update a thing"""
    statement = select(Thing).where(Thing.id == id)
    db_thing = session.exec(statement).first()

    if db_thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"thing with id: {id} does not exist",
        )

    thing_data = thing.model_dump(exclude_unset=True)
    for key, value in thing_data.items():
        setattr(db_thing, key, value)

    session.add(db_thing)
    session.commit()
    session.refresh(db_thing)

    return db_thing


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_thing(
    id: Annotated[int, Path(description="The ID of the thing to delete")],
    session: Session = Depends(get_session),
):
    """
    Delete a specific thing identified by its id
    """
    statement = select(Thing).where(Thing.id == id)
    thing = session.exec(statement).first()

    if thing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thing with id: {id} does not exist",
        )

    session.delete(thing)
    session.commit()

    return
