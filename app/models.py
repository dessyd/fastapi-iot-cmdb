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

class LocationResponse(Thing):
    id = int
    provisioned_at = datetime

# Locations

class LocationBase(BaseModel):
    name: str
    lat: float
    lon: float

class Loacation(LocationBase):
    pass 

class LocationResponse(Loacation):
    id = int


