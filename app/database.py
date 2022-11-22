from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

SQLALCHEMY_DATABASE_URL = f"{settings.database_driver}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Init DB see: https://www.andrewvillazon.com/move-data-to-db-with-sqlalchemy/
# def init_db(db: Session = Depends(get_db)):

#     with open('init/boards.csv', encoding='utf-8', newline='') as csv_file:
#         csvreader = csv.DictReader(csv_file, quotechar='"')
#         listings = [Board(**row) for row in csvreader]

#         db.add_all(listings)
#         db.commit()
