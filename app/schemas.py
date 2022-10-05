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

class LocationUpdate(LocationBase):
    pass 

class LocationJoin(LocationBase):
    pass

    class Config:
        orm_mode = True


class LocationOut(LocationBase):
    id : int
    created_at: datetime

    class Config:
        orm_mode = True

# Things

class ThingBase(BaseModel):
    mac: str
    name: str

class ThingCreate(ThingBase):
    location_id: int
    pass

class ThingUpdate(ThingBase):
    pass

class ThingOut(ThingCreate):
    id : int
    created_at: datetime
    location: LocationJoin

    class Config:
        orm_mode = True

