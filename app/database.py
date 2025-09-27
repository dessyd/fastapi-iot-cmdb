from sqlmodel import Session, SQLModel, create_engine

from .config import settings

DATABASE_URL = f"{settings.database_driver}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging during development
    pool_pre_ping=True,
    pool_recycle=300,
)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session


# Init DB see: https://www.andrewvillazon.com/move-data-to-db-with-sqlalchemy/
# def init_db(db: Session = Depends(get_db)):

#     with open('init/boards.csv', encoding='utf-8', newline='') as csv_file:
#         csvreader = csv.DictReader(csv_file, quotechar='"')
#         listings = [Board(**row) for row in csvreader]

#         db.add_all(listings)
#         db.commit()
