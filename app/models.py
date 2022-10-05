from ast import In
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from .database import Base

class Thing(Base):
    __tablename__ = "things"
    id = Column(Integer, primary_key=True, nullable=False)
    mac = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    location = relationship("Location")

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False, default=0.0)
    lon = Column(Float, nullable=False, default=0.0)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    