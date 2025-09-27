import re
from datetime import datetime
from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


# Location Models
class LocationBase(SQLModel):
    """Base model with shared location fields"""

    name: str = Field(min_length=1, max_length=255, description="Location name")
    lat: float = Field(default=0.0, ge=-90, le=90, description="Latitude coordinate")
    lon: float = Field(default=0.0, ge=-180, le=180, description="Longitude coordinate")


class Location(LocationBase, table=True):
    """Database table model for locations"""

    __tablename__ = "locations"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    things: List["Thing"] = Relationship(back_populates="location")


class LocationCreate(LocationBase):
    """Model for creating new locations"""


class LocationUpdate(SQLModel):
    """Model for updating locations (all fields optional)"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)


class LocationRead(LocationBase):
    """Model for reading locations (includes generated fields)"""

    id: int
    created_at: datetime


class LocationReadWithThings(LocationRead):
    """Model for reading locations with their things"""

    things: List["ThingRead"] = []


# Thing Models
class ThingBase(SQLModel):
    """Base model with shared thing fields"""

    mac: str = Field(description="MAC address in XX:XX:XX:XX:XX:XX format")
    name: str = Field(min_length=1, max_length=255, description="Device name")

    @field_validator("mac")
    @classmethod
    def validate_mac_address(cls, v):
        pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not re.match(pattern, v):
            raise ValueError("Invalid MAC address format. Use XX:XX:XX:XX:XX:XX")
        return v


class Thing(ThingBase, table=True):
    """Database table model for things"""

    __tablename__ = "things"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    location_id: int = Field(foreign_key="locations.id", description="Associated location ID")

    # Relationships
    location: Optional[Location] = Relationship(back_populates="things")


class ThingCreate(ThingBase):
    """Model for creating new things"""

    location_id: int


class ThingUpdate(SQLModel):
    """Model for updating things (all fields optional)"""

    mac: Optional[str] = Field(default=None, description="MAC address")
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)

    @field_validator("mac")
    @classmethod
    def validate_mac_address(cls, v):
        if v is not None:
            pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
            if not re.match(pattern, v):
                raise ValueError("Invalid MAC address format. Use XX:XX:XX:XX:XX:XX")
        return v


class ThingRead(ThingBase):
    """Model for reading things (includes generated fields)"""

    id: int
    created_at: datetime
    location_id: int


class ThingReadWithLocation(ThingRead):
    """Model for reading things with their location"""

    location: Optional[LocationRead] = None
