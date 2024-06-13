import sqlalchemy
import sqlmodel

import models
import services.qdrant


def delete_by_name(db_session: sqlmodel.Session, name: str) -> tuple[int, int]:
    """
    Delete corpus object and all attached data, including:
      - postgres tables used for indices
      - qdrant vector store persisted via qdrant server
    """
    model = models.Corpus
    dataset = sqlmodel.select(model)

    dataset = dataset.where(model.name == name)
    corpus = db_session.exec(dataset).first()

    if not corpus:
        return 404, 404

    try:
        # delete qdrant store(s)
        if corpus.vector_img_uri:
            collection = corpus.vector_img_uri.split(":")[-1]
            client = services.qdrant.client()

            if not client.delete_collection(collection):
                qdrant_code = 404
            else:
                qdrant_code = 0

        if corpus.vector_txt_uri:
            collection = corpus.vector_txt_uri.split(":")[-1]
            client = services.qdrant.client()

            if not client.delete_collection(collection):
                qdrant_code = 404
            else:
                qdrant_code = 0
    except Exception:
        qdrant_code = 500

    # delete postgres index tables

    for table_name in corpus.storage_keyword_tables:
        db_session.execute(sqlalchemy.text(f"drop table if exists {table_name}"))

    # delete corpus object

    db_session.delete(corpus)
    db_session.commit()

    return 0, qdrant_code



