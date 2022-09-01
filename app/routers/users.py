from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=models.UserOut)
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)
    # stores hashed password back
    user.password = hashed_password

    new_user = schemas.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=models.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(schemas.User).filter(schemas.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} is unknown"
        )

    return user
