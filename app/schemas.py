from datetime import datetime

from pydantic import BaseModel

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
        from_attributes = True


class LocationOut(LocationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Things


class ThingBase(BaseModel):
    mac: str
    name: str


class ThingCreate(ThingBase):
    location_id: int


class ThingUpdate(ThingBase):
    pass


class ThingOut(ThingCreate):
    id: int
    created_at: datetime
    location: LocationJoin

    class Config:
        from_attributes = True


class BoardBase(BaseModel):
    id: int
    name: str


class SensorBase(BaseModel):
    id: int
    name: str
