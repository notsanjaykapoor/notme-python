import sqlalchemy
import sqlmodel

import models
import services.milvus


def delete_by_name(db_session: sqlmodel.Session, name: str) -> tuple:
    """
    Delete corpus object from milvus and postgres dbs
    """
    try:
        milvus_code = services.milvus.delete_by_name(collection=name)
    except Exception:
        milvus_code = 500

    # its possible that postgres object exists even if milvus object doesn't

    model = models.Corpus
    dataset = sqlmodel.select(model)

    dataset = dataset.where(model.name == name)
    corpus = db_session.exec(dataset).first()

    if not corpus:
        return milvus_code, 404

    # delete index tables

    for table_name in corpus.keyword_tables:
        db_session.execute(sqlalchemy.text(f"drop table if exists {table_name}"))

    # delete corpus object

    db_session.delete(corpus)
    db_session.commit()

    return milvus_code, 0



