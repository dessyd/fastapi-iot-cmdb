# SQLModel Complete Rewrite Implementation Plan

## Overview

This document outlines a complete rewrite of the FastAPI IoT CMDB using SQLModel from the ground up. Instead of migrating from SQLAlchemy + Pydantic, we'll rebuild the entire data layer with SQLModel's unified approach, eliminating code duplication and improving type safety.

## Current Architecture Analysis

### Current Problems
- **Duplicate field definitions**: Same fields defined in both SQLAlchemy models and Pydantic schemas
- **Complex schema hierarchy**: 10+ schema classes for 4 data models
- **Inconsistent patterns**: Mixed async/sync operations
- **Maintenance overhead**: Changes require updates in multiple places

### Current Structure
```
Current (SQLAlchemy + Pydantic):
- models.py: 4 SQLAlchemy classes (38 lines)
- schemas.py: 10+ Pydantic classes (70 lines)
- Total: ~108 lines for data definitions

Future (SQLModel):
- models.py: 4-6 unified classes (~60 lines)
- Total: ~60 lines for data definitions
- Reduction: ~45% less code
```

## SQLModel Rewrite Benefits

### 1. Unified Model Architecture
- **Single source of truth**: One class serves as both database model and API schema
- **Type consistency**: Same types across database operations and API responses
- **Automatic validation**: Built-in Pydantic validation for database models

### 2. Simplified Class Structure
**Before (SQLAlchemy + Pydantic)**:
- `Location` (SQLAlchemy model)
- `LocationBase`, `LocationCreate`, `LocationUpdate`, `LocationJoin`, `LocationOut` (5 Pydantic schemas)
- Total: 6 classes per entity

**After (SQLModel)**:
- `LocationBase` (shared fields)
- `Location` (table model)
- `LocationCreate`, `LocationUpdate`, `LocationRead` (API models)
- Total: 4 classes per entity (33% reduction)

### 3. Enhanced Type Safety
- **IDE autocompletion**: Better IntelliSense support
- **Runtime validation**: Automatic field validation on database operations
- **Relationship typing**: Proper type hints for foreign key relationships

## Implementation Plan

### Phase 1: Dependencies and Configuration

#### 1.1 Update Dependencies
```python
# requirements.txt changes
- sqlalchemy
- pydantic
+ sqlmodel>=0.0.8  # Includes both SQLAlchemy and Pydantic
```

#### 1.2 Database Configuration Rewrite
**New `app/database.py`**:
```python
from sqlmodel import create_engine, SQLModel, Session
from .config import settings

# Database URL construction
DATABASE_URL = f"{settings.database_driver}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# Engine creation
engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300
)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
```

**Key Changes**:
- Replace `SessionLocal` with SQLModel's `Session`
- Remove `Base` declarative class (SQLModel handles this)
- Simplified session management with context manager

### Phase 2: Model Rewrite with SQLModel

#### 2.1 Unified Location Models
**New approach** - Single file with all Location-related classes:

```python
# app/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

# Base model with shared fields
class LocationBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    lat: float = Field(default=0.0, ge=-90, le=90)
    lon: float = Field(default=0.0, ge=-180, le=180)

# Database table model
class Location(LocationBase, table=True):
    __tablename__ = "locations"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    things: List["Thing"] = Relationship(back_populates="location")

# API models
class LocationCreate(LocationBase):
    """Model for creating new locations"""
    pass

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
    """Model for reading locations with relationships"""
    things: List["ThingRead"] = []
```

#### 2.2 Unified Thing Models
```python
class ThingBase(SQLModel):
    mac: str = Field(regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    name: str = Field(min_length=1, max_length=255)

class Thing(ThingBase, table=True):
    __tablename__ = "things"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    location_id: int = Field(foreign_key="locations.id")

    # Relationships
    location: Optional[Location] = Relationship(back_populates="things")

class ThingCreate(ThingBase):
    location_id: int

class ThingUpdate(SQLModel):
    mac: Optional[str] = Field(default=None, regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)

class ThingRead(ThingBase):
    id: int
    created_at: datetime
    location_id: int

class ThingReadWithLocation(ThingRead):
    location: Optional[LocationRead] = None
```

#### 2.3 Board and Sensor Models
```python
class BoardBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)

class Board(BoardBase, table=True):
    __tablename__ = "boards"

    id: Optional[int] = Field(default=None, primary_key=True)

class BoardCreate(BoardBase):
    pass

class BoardRead(BoardBase):
    id: int

class SensorBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)

class Sensor(SensorBase, table=True):
    __tablename__ = "sensors"

    id: Optional[int] = Field(default=None, primary_key=True)

class SensorCreate(SensorBase):
    pass

class SensorRead(SensorBase):
    id: int
```

### Phase 3: Database Operations Rewrite

#### 3.1 SQLModel Query Patterns
**Before (SQLAlchemy)**:
```python
# Complex query syntax
location = db.query(models.Location).filter(models.Location.id == id).first()
```

**After (SQLModel)**:
```python
# Simplified query syntax
from sqlmodel import select

statement = select(Location).where(Location.id == id)
location = session.exec(statement).first()
```

#### 3.2 CRUD Operations Patterns

**Create Operations**:
```python
# Before
new_location = models.Location(**location.model_dump())
db.add(new_location)
db.commit()
db.refresh(new_location)

# After
db_location = Location.model_validate(location)
session.add(db_location)
session.commit()
session.refresh(db_location)
```

**Read Operations**:
```python
# Single record
statement = select(Location).where(Location.id == location_id)
location = session.exec(statement).first()

# Multiple records
statement = select(Location)
locations = session.exec(statement).all()

# With relationships
statement = select(Location).options(selectinload(Location.things))
location = session.exec(statement).first()
```

**Update Operations**:
```python
# Before
location_query.update(jsonable_encoder(location), synchronize_session=False)

# After
statement = select(Location).where(Location.id == location_id)
db_location = session.exec(statement).first()
location_data = location.model_dump(exclude_unset=True)
for key, value in location_data.items():
    setattr(db_location, key, value)
session.add(db_location)
session.commit()
session.refresh(db_location)
```

### Phase 4: Router Rewrite

#### 4.1 Location Router with SQLModel
```python
from sqlmodel import Session, select
from ..models import Location, LocationCreate, LocationUpdate, LocationRead

@router.get("/", response_model=List[LocationRead])
async def get_all_locations(session: Session = Depends(get_session)):
    """Get all locations"""
    statement = select(Location)
    locations = session.exec(statement).all()
    return locations

@router.get("/{id}", response_model=LocationRead)
async def get_location(
    id: int = Path(description="The ID of the location to get"),
    session: Session = Depends(get_session)
):
    """Get a specific location by ID"""
    statement = select(Location).where(Location.id == id)
    location = session.exec(statement).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location with id {id} not found")
    return location

@router.post("/", response_model=LocationRead, status_code=201)
async def create_location(
    location: LocationCreate,
    session: Session = Depends(get_session)
):
    """Create a new location"""
    db_location = Location.model_validate(location)
    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    return db_location
```

#### 4.2 Thing Router with SQLModel
```python
@router.get("/", response_model=List[ThingReadWithLocation])
async def get_all_things(session: Session = Depends(get_session)):
    """Get all things with their locations"""
    statement = select(Thing).options(selectinload(Thing.location))
    things = session.exec(statement).all()
    return things

@router.post("/", response_model=ThingRead, status_code=201)
async def create_thing(
    thing: ThingCreate,
    session: Session = Depends(get_session)
):
    """Create a new thing"""
    # Validate location exists
    location_statement = select(Location).where(Location.id == thing.location_id)
    location = session.exec(location_statement).first()
    if not location:
        raise HTTPException(status_code=400, detail="Location not found")

    db_thing = Thing.model_validate(thing)
    session.add(db_thing)
    session.commit()
    session.refresh(db_thing)
    return db_thing
```

### Phase 5: Async/Sync Operations Impact

#### 5.1 Current State
- **Mixed patterns**: Some functions async, some sync
- **No async database operations**: Using sync SQLAlchemy sessions

#### 5.2 SQLModel Async Recommendations

**Option A: Stay Sync (Recommended for simplicity)**
```python
# Continue with sync operations
def get_session():
    with Session(engine) as session:
        yield session

# Router functions can stay async for FastAPI compatibility
@router.get("/")
async def get_locations(session: Session = Depends(get_session)):
    # Sync database operations inside async function
    statement = select(Location)
    return session.exec(statement).all()
```

**Option B: Full Async (For high concurrency)**
```python
from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Async engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session

@router.get("/")
async def get_locations(session: AsyncSession = Depends(get_async_session)):
    statement = select(Location)
    result = await session.exec(statement)
    return result.all()
```

**Recommendation**: Start with **Option A** (sync) for simplicity, migrate to async only if performance testing shows bottlenecks.

### Phase 6: Validation and Error Handling

#### 6.1 Enhanced Validation
SQLModel provides automatic validation:

```python
class ThingBase(SQLModel):
    mac: str = Field(
        regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
        description="MAC address in XX:XX:XX:XX:XX:XX format"
    )
    name: str = Field(min_length=1, max_length=255, description="Device name")

# Automatic validation on creation
thing = ThingCreate(mac="invalid", name="")  # Raises ValidationError
```

#### 6.2 Database Constraint Handling
```python
from sqlalchemy.exc import IntegrityError

@router.post("/")
async def create_thing(thing: ThingCreate, session: Session = Depends(get_session)):
    try:
        db_thing = Thing.model_validate(thing)
        session.add(db_thing)
        session.commit()
        session.refresh(db_thing)
        return db_thing
    except IntegrityError as e:
        session.rollback()
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Invalid location_id")
        raise HTTPException(status_code=400, detail="Database constraint violation")
```

## Implementation Checklist

### Phase 1: Setup
- [ ] Install SQLModel (`pip install sqlmodel`)
- [ ] Remove old dependencies (sqlalchemy, pydantic)
- [ ] Rewrite `database.py` with SQLModel patterns

### Phase 2: Models
- [ ] Create unified Location models
- [ ] Create unified Thing models
- [ ] Create unified Board models
- [ ] Create unified Sensor models
- [ ] Add comprehensive field validation

### Phase 3: Database Operations
- [ ] Rewrite all SELECT queries with SQLModel syntax
- [ ] Rewrite all INSERT operations
- [ ] Rewrite all UPDATE operations
- [ ] Rewrite all DELETE operations
- [ ] Add relationship loading patterns

### Phase 4: Routers
- [ ] Update location router with new models and session
- [ ] Update thing router with new models and session
- [ ] Add proper error handling for validation
- [ ] Add constraint violation handling

### Phase 5: Testing and Validation
- [ ] Test all CRUD operations
- [ ] Test relationship loading
- [ ] Test validation errors
- [ ] Test database constraints
- [ ] Verify API documentation generation

## Class Simplification Summary

### Before (Current)
```
Location ecosystem:
- models.Location (SQLAlchemy)
- schemas.LocationBase
- schemas.LocationCreate
- schemas.LocationUpdate
- schemas.LocationJoin
- schemas.LocationOut
Total: 6 classes

Thing ecosystem:
- models.Thing (SQLAlchemy)
- schemas.ThingBase
- schemas.ThingCreate
- schemas.ThingUpdate
- schemas.ThingOut
Total: 5 classes

Overall: 11 classes for 2 entities
```

### After (SQLModel)
```
Location ecosystem:
- LocationBase (shared fields)
- Location (table model)
- LocationCreate (API input)
- LocationUpdate (API update)
- LocationRead (API output)
Total: 5 classes (-17% reduction)

Thing ecosystem:
- ThingBase (shared fields)
- Thing (table model)
- ThingCreate (API input)
- ThingUpdate (API update)
- ThingRead (API output)
- ThingReadWithLocation (with relationships)
Total: 6 classes (+20% for better relationship handling)

Overall: 11 classes for 2 entities (same count, but unified functionality)
```

### Code Reduction Benefits
- **Field definitions**: No duplication between models and schemas
- **Validation logic**: Single definition with automatic API/DB validation
- **Type hints**: Consistent across all layers
- **Maintenance**: Single place to update field definitions

## Database Operations Impact

### Query Simplification
**Before**:
```python
location = db.query(models.Location).filter(models.Location.id == id).first()
things = db.query(models.Thing).filter(models.Thing.location_id == location_id).all()
```

**After**:
```python
location = session.exec(select(Location).where(Location.id == id)).first()
things = session.exec(select(Thing).where(Thing.location_id == location_id)).all()
```

### Relationship Loading
**Before**:
```python
# Manual joins or separate queries
location = db.query(models.Location).filter(models.Location.id == id).first()
# Location.things relationship not typed
```

**After**:
```python
# Explicit relationship loading with proper typing
statement = select(Location).options(selectinload(Location.things)).where(Location.id == id)
location = session.exec(statement).first()
# location.things is properly typed as List[Thing]
```

## Async/Sync Operations Impact

### Current Mixed Pattern
```python
# Some functions async, some sync - inconsistent
@router.get("/")
async def get_all_locations(db: Session = Depends(get_db)):  # async function
    locations = db.query(models.Location).all()  # sync operation
    return locations

@router.put("/{id}")
def update_location(id: int, location: schemas.LocationUpdate):  # sync function
    # sync operations
```

### SQLModel Recommendation: Consistent Async
```python
# All router functions async for FastAPI consistency
@router.get("/")
async def get_all_locations(session: Session = Depends(get_session)):
    statement = select(Location)
    locations = session.exec(statement).all()  # sync DB operation in async function
    return locations

@router.put("/{id}")
async def update_location(id: int, location: LocationUpdate, session: Session = Depends(get_session)):
    # All functions follow same async pattern
```

### Benefits of Consistent Pattern
- **Predictable code structure**: All endpoints follow same pattern
- **Better FastAPI integration**: Async functions work better with FastAPI middleware
- **Future async migration**: Easy to migrate to async DB operations later
- **Testing consistency**: All tests can use same async patterns

## Success Metrics

### Code Quality
- [ ] 40-50% reduction in model definition lines
- [ ] Eliminated duplicate field definitions
- [ ] 100% type safety across data layer
- [ ] Single source of truth for each entity

### Functionality
- [ ] All current API endpoints work identically
- [ ] All database operations preserved
- [ ] All relationships work correctly
- [ ] All validation rules maintained

### Performance
- [ ] No performance degradation in CRUD operations
- [ ] Improved validation performance (compiled Pydantic models)
- [ ] Better memory usage (unified model instances)

---

**Note**: This rewrite leverages SQLModel's core advantage - eliminating the boundary between database models and API schemas while maintaining full type safety and validation across the entire application stack.
