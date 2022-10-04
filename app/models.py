from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic.types import conint

# Things

class ThingBase(BaseModel):

    name = str
    description = str
    enabled = bool = True
    location_id = int

class Thing(ThingBase):
    pass 

class ThingResponse(Thing):
    id = int
    provisioned_at = datetime
    class Config:
        orm_mode = True

# Locations

class LocationBase(BaseModel):
    name: str
    lat: float
    lon: float

class Location(LocationBase):
    pass 

class LocationResponse(Location):
    id = int
    class Config:
        orm_mode = True

