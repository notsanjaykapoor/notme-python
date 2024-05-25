import sqlmodel

import models


def get_by_id(db_session: sqlmodel.Session, id: int) -> models.Corpus | None:
    """
    """
    db_select = sqlmodel.select(models.Corpus).where(models.Corpus.id == id)
    return db_session.exec(db_select).first()


def get_by_name(db_session: sqlmodel.Session, name: str) -> models.Corpus | None:
    """
    """
    db_select = sqlmodel.select(models.Corpus).where(models.Corpus.name == name)
    return db_session.exec(db_select).first()


def get_by_source_uri(db_session: sqlmodel.Session, source_uri: str) -> models.Corpus | None:
    """
    """
    db_select = sqlmodel.select(models.Corpus).where(models.Corpus.source_uri == source_uri)
    return db_session.exec(db_select).first()

