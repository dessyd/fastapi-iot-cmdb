from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas, utils

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=models.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)
):

    db_user = db.query(schemas.User).filter(schemas.User.email == user_credentials.username).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(user_credentials.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": db_user.id})

    return {"access_token": access_token, "token_type": "bearer"}
