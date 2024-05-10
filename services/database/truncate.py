import sqlalchemy
import sqlmodel

from .session import table_names


def truncate_all(db: sqlmodel.Session, exclude: list[str] = ["credentials", "spatial_ref_sys", "users"]):
    for table_name in table_names():
        if table_name not in exclude:
            truncate_table(db, table_name)


def truncate_table(db: sqlmodel.Session, table_name: str):
    db.execute(sqlalchemy.text(f"delete from {table_name}"))
    db.commit()
