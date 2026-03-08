from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ect_app.config import settings


class Base(DeclarativeBase):
    pass


def _build_engine_kwargs() -> dict:
    kwargs: dict = {}
    if settings.database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


engine = create_engine(settings.database_url, **_build_engine_kwargs())
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so Base.metadata discovers them
    import ect_app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
