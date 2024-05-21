import typing

import sqlmodel

import models


def get_by_id(db_session: sqlmodel.Session, id: int) -> typing.Optional[models.Corpus]:
    """
    """
    db_select = sqlmodel.select(models.Corpus).where(models.Corpus.id == id)
    db_object = db_session.exec(db_select).first()

    return db_object


def get_by_name(db_session: sqlmodel.Session, name: str) -> typing.Optional[models.Corpus]:
    """
    """
    db_select = sqlmodel.select(models.Corpus).where(models.Corpus.name == name)
    db_object = db_session.exec(db_select).first()

    return db_object


def get_by_source_dir(db_session: sqlmodel.Session, source_dir: str) -> typing.Optional[models.Corpus]:
    """
    """
    db_select = sqlmodel.select(models.Corpus).where(models.Corpus.source_dir == source_dir)
    db_object = db_session.exec(db_select).first()

    return db_object


def epoch_generate(db_session: sqlmodel.Session, name_encoded: str, default: int=1) -> int:
    """
    """
    db_object = get_by_name(db_session=db_session, name=name_encoded)

    if db_object:
        return db_object.epoch + 1
    else:
        return default
