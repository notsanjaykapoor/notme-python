from sqlmodel import Session


def truncate_table(db: Session, table_name: str):
    db.execute(f"delete from {table_name}")
    db.commit()
