import timescaledb
from sqlalchemy import text
from sqlmodel import Session, SQLModel

from .config import DATABASE_URL, DB_TIMEZONE, PGCRYPTO_KEY

if DATABASE_URL == "":
    raise NotImplementedError("DATABASE_URL needs to be set")

if PGCRYPTO_KEY == "":
    raise NotImplementedError("PGCRYPTO_KEY needs to be set for encryption")

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
    print("initializing pgcrypto encryption trigger")
    init_pgcrypto_trigger()


def init_pgcrypto_trigger():
    """Initialize pgcrypto extension and create encryption trigger for users table.

    This function:
    1. Enables the pgcrypto extension
    2. Sets the encryption key in PostgreSQL session settings
    3. Creates the trigger function and trigger for automatic field encryption
    4. Called during application startup via init_db()
    """
    with Session(engine) as session:
        try:
            # Set the encryption key in PostgreSQL session settings
            # The trigger function reads this via current_setting()
            session.exec(
                text("SELECT set_config(:key_name, :key_value, false)").bindparams(
                    key_name="app.pgcrypto_key", key_value=PGCRYPTO_KEY
                )
            )

            # Read and execute the trigger SQL file
            import os

            trigger_sql_path = os.path.join(os.path.dirname(__file__), "triggers.sql")

            with open(trigger_sql_path, "r") as f:
                trigger_sql = f.read()

            # Execute the trigger creation SQL
            session.exec(text(trigger_sql))
            session.commit()
            print("✅ pgcrypto extension and encryption trigger initialized")

        except Exception as e:
            print(f"⚠️ Error initializing pgcrypto trigger: {e}")
            session.rollback()


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
