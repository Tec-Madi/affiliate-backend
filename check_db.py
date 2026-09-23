from core.config import AISHORASUB_DATABASE_URL
from sqlalchemy import create_engine, text

engine = create_engine(AISHORASUB_DATABASE_URL)

with engine.connect() as conn:
    rows = conn.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'users'
            ORDER BY ordinal_position
        """)
    ).fetchall()

    print(rows)