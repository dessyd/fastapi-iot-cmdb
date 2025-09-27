# SQLModel Migration Plan

## Overview

This document outlines the detailed migration plan for converting the FastAPI IoT CMDB from pure SQLAlchemy + Pydantic to SQLModel. This migration will unify our data models, reduce code duplication, and improve type safety while maintaining all existing functionality.

## Current Architecture Analysis

### Current Stack
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Alembic**: Database migrations
- **PostgreSQL**: Database backend

### Current File Structure
```
app/
├── main.py              # FastAPI app with custom OpenAPI
├── config.py            # Database configuration
├── database.py          # SQLAlchemy setup
├── models.py            # SQLAlchemy models (Thing, Location, Board, Sensor)
├── schemas.py           # Pydantic schemas (separate from models)
└── routers/
    ├── locations.py     # Location CRUD endpoints
    └── things.py        # Thing CRUD endpoints
```

### Current Models & Schemas
- **Models**: 4 SQLAlchemy classes (Thing, Location, Board, Sensor)
- **Schemas**: 10+ Pydantic classes (Base, Create, Update, Out, Join variants)
- **Duplication**: Field definitions repeated between models and schemas

## Migration Benefits

### 1. Code Reduction
- **Eliminate duplicate field definitions** between SQLAlchemy models and Pydantic schemas
- **Reduce schema classes** from 10+ to ~6-8 unified models
- **Simplify maintenance** with single source of truth for data structures

### 2. Type Safety Improvements
- **Enhanced IDE support** with better autocompletion and error detection
- **Consistent typing** across database and API layers
- **Runtime validation** integrated with database models

### 3. Developer Experience
- **Unified model definitions** that work for both database and API
- **Better error messages** with integrated validation
- **Simplified testing** with consistent data structures

## Migration Strategy

### Phase 1: Dependencies and Setup
1. **Add SQLModel dependency**
   ```bash
   pip install sqlmodel
   ```

2. **Update requirements.txt**
   ```
   sqlmodel>=0.0.8
   ```

3. **Verify compatibility**
   - Ensure SQLModel works with current FastAPI version
   - Test Alembic compatibility with SQLModel

### Phase 2: Model Migration

#### 2.1 Create New SQLModel Models
Create new models in `app/models_sqlmodel.py`:

```python
# New unified models combining SQLAlchemy + Pydantic
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class LocationBase(SQLModel):
    name: str
    lat: float = 0.0
    lon: float = 0.0

class Location(LocationBase, table=True):
    __tablename__ = "locations"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    things: list["Thing"] = Relationship(back_populates="location")

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    pass

class ThingBase(SQLModel):
    mac: str
    name: str
    location_id: int = Field(foreign_key="locations.id")

class Thing(ThingBase, table=True):
    __tablename__ = "things"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    location: Optional[Location] = Relationship(back_populates="things")

class ThingCreate(ThingBase):
    pass

class ThingUpdate(SQLModel):
    mac: Optional[str] = None
    name: Optional[str] = None

# Response models with relationships
class LocationRead(LocationBase):
    id: int
    created_at: datetime

class ThingRead(ThingBase):
    id: int
    created_at: datetime
    location: Optional[LocationRead] = None
```

#### 2.2 Migrate Remaining Models
- **Board**: Convert to SQLModel format
- **Sensor**: Convert to SQLModel format
- **Future models**: Follow SQLModel patterns

### Phase 3: Database Layer Migration

#### 3.1 Update Database Configuration
Modify `app/database.py`:

```python
from sqlmodel import create_engine, SQLModel, Session
from .config import settings

# Engine creation (compatible with SQLModel)
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

#### 3.2 Update Dependency Injection
Replace `get_db()` with `get_session()` across all routers.

### Phase 4: Router Migration

#### 4.1 Update Location Router
```python
from sqlmodel import Session, select
from ..models_sqlmodel import Location, LocationCreate, LocationUpdate, LocationRead

@router.get("/", response_model=List[LocationRead])
async def get_all_locations(session: Session = Depends(get_session)):
    statement = select(Location)
    locations = session.exec(statement).all()
    return locations

@router.post("/", response_model=LocationRead)
async def create_location(location: LocationCreate, session: Session = Depends(get_session)):
    db_location = Location.from_orm(location)
    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    return db_location
```

#### 4.2 Update Thing Router
- Convert all CRUD operations to use SQLModel syntax
- Update type hints and response models
- Maintain relationship loading patterns

### Phase 5: Schema Cleanup

#### 5.1 Remove Obsolete Files
- **Delete**: `app/schemas.py` (replaced by unified models)
- **Archive**: `app/models.py` → `app/models_legacy.py` (backup)

#### 5.2 Update Imports
- Replace `from ..schemas import` with `from ..models_sqlmodel import`
- Update all router files with new import paths

### Phase 6: Alembic Migration

#### 6.1 Generate Migration
```bash
alembic revision --autogenerate -m "Migrate to SQLModel"
```

#### 6.2 Verify Migration
- Check generated migration for correctness
- Ensure no data loss during schema changes
- Test migration on development database

### Phase 7: Testing and Validation

#### 7.1 API Testing
- **Endpoint validation**: Ensure all endpoints work with new models
- **Response verification**: Confirm JSON output remains identical
- **Relationship testing**: Verify foreign key relationships work correctly

#### 7.2 Database Testing
- **CRUD operations**: Test all Create, Read, Update, Delete operations
- **Migration testing**: Verify Alembic migrations work correctly
- **Performance testing**: Compare query performance before/after

## Implementation Checklist

### Prerequisites
- [ ] Create SQLModel branch
- [ ] Research SQLModel best practices
- [ ] Document current API behavior for testing

### Migration Steps
- [ ] Install SQLModel dependency
- [ ] Create unified models in `models_sqlmodel.py`
- [ ] Update database configuration
- [ ] Migrate location router
- [ ] Migrate things router
- [ ] Update main.py imports
- [ ] Generate Alembic migration
- [ ] Test all endpoints
- [ ] Update tests
- [ ] Clean up legacy files

### Validation Steps
- [ ] All tests pass
- [ ] API documentation generates correctly
- [ ] Database migrations work
- [ ] Performance is maintained or improved
- [ ] Type checking passes

## Risk Assessment

### Low Risk
- **Alembic compatibility**: SQLModel works well with Alembic
- **FastAPI integration**: SQLModel was designed for FastAPI
- **Database compatibility**: Uses SQLAlchemy under the hood

### Medium Risk
- **Relationship definitions**: May need adjustment in complex scenarios
- **Custom field types**: Need verification with SQLModel
- **Performance impact**: Should be minimal but requires testing

### Mitigation Strategies
- **Backup database** before migration
- **Parallel implementation** - keep old models during transition
- **Gradual rollout** - migrate one router at a time
- **Comprehensive testing** at each step

## Timeline Estimate

### Development: 2-3 days
- Day 1: Model creation and database setup
- Day 2: Router migration and testing
- Day 3: Cleanup and final validation

### Testing: 1 day
- Integration testing
- Performance validation
- Migration testing

### Total: 3-4 days

## Post-Migration Benefits

### Immediate
- **Reduced codebase size** (estimated 30-40% reduction in model/schema code)
- **Better type safety** across the application
- **Simplified maintenance** with unified models

### Long-term
- **Easier feature development** with less boilerplate
- **Better developer onboarding** with simpler patterns
- **Enhanced IDE support** for better productivity

## Rollback Plan

If migration issues arise:

1. **Revert to main branch**: `git checkout main`
2. **Restore database**: From pre-migration backup
3. **Document issues**: For future migration attempts

## Success Metrics

- [ ] All existing API functionality preserved
- [ ] Reduced lines of code in model definitions
- [ ] No performance degradation
- [ ] All tests pass
- [ ] Documentation generates correctly
- [ ] Type checking improvements verified

---

**Note**: This migration leverages SQLModel's core strength - unifying SQLAlchemy and Pydantic into a single, type-safe model definition while maintaining full compatibility with FastAPI and existing database operations.
