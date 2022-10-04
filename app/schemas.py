from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

# Locations

class LocationBase(BaseModel):
    name: str
    lat: float
    lon: float

class LocationCreate(LocationBase):
    pass 

class LocationOut(LocationBase):

    id : int
    created_at: datetime

    class Config:
        orm_mode = True

