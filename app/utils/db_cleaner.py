# app/utils/db_cleaner.py

from sqlalchemy import MetaData
from app.database.session import engine

def clear_all_data():
    """
    Deletes all data from all tables in the database (but keeps the table structure).
    """
    meta = MetaData()
    meta.reflect(bind=engine)  # Load table metadata from DB

    with engine.begin() as conn:
        for table in reversed(meta.sorted_tables):
            conn.execute(table.delete())  # Delete all rows from the table
