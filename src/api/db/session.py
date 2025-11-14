import timescaledb
from sqlmodel import Session, SQLModel

from .config import DATABASE_URL, DB_TIMEZONE

if DATABASE_URL == "":
    raise NotImplementedError("DATABASE_URL needs to be set")

engine = timescaledb.create_engine(DATABASE_URL, timezone=DB_TIMEZONE)


def init_db():
    """Initialize the database with SQLModel and TimescaleDB schemas.

    Creates all SQLModel tables and TimescaleDB hypertables configured
    in the application's models. This function is called during app startup
    via the lifespan context manager in main.py."""

    print("creating database")
    SQLModel.metadata.create_all(engine)
    print("creating hypertables")
    timescaledb.metadata.create_all(engine)


def get_session():
    """Provide a database session for dependency injection.

    Yields a SQLModel Session instance bound to the TimescaleDB engine.
    This is used as a FastAPI dependency in route handlers to get
    database access. The session is automatically closed after use.

    Yields:
        Session: A SQLModel session for executing database queries.
    """
    with Session(engine) as session:
        yield session
