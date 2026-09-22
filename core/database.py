from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import (
    AISHORASUB_DATABASE_URL,
    MEERALINKS_DATABASE_URL,
    HZQUICKLINK_DATABASE_URL,
)


def create_db_engine(url: str):
    return create_engine(
        url,
        connect_args={"prepare_threshold": None},
    )

aishorasub_engine = create_db_engine(AISHORASUB_DATABASE_URL)
meeralinks_engine = create_db_engine(MEERALINKS_DATABASE_URL)
hzquicklink_engine = create_db_engine(HZQUICKLINK_DATABASE_URL)

aishorasub_session = sessionmaker(bind=aishorasub_engine)
meeralinks_session = sessionmaker(bind=meeralinks_engine)
hzquicklink_session = sessionmaker(bind=hzquicklink_engine)

DB_MAP = {
    "api.aishorasub.com": aishorasub_session,
    "api.meeralinks.com": meeralinks_session,
    "api.hzquicklink.com": hzquicklink_session,
}

class Base(DeclarativeBase):
    pass

def get_db(request: Request):
    session_factory = DB_MAP.get(request.url.hostname)

    if not session_factory:
        raise ValueError("Unknown API hostname")

    db: Session = session_factory()

    try:
        yield db
    finally:
        db.close()