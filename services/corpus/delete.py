import sqlalchemy
import sqlalchemy_utils.functions


def delete(db_url: str, db_name: str) -> int:
    """
    Delete corpus database
    """
    db_name_url = f"{db_url}/{db_name}"
    engine = sqlalchemy.create_engine(db_name_url, echo=False)

    if not sqlalchemy_utils.functions.database_exists(engine.url):
        return 404

    sqlalchemy_utils.functions.drop_database(engine.url)

    return 0


