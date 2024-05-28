import os

import models
import sqlmodel

import services.corpus


def init(db_session: sqlmodel.Session, corpus_id: int, source_uri: str, model: str, splitter: str) -> models.Corpus:
    """
    
    """
    if corpus_id:
        corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)
    else:
        corpus = services.corpus.get_by_source_uri(db_session=db_session, source_uri=source_uri)

    if corpus:
        # update corpus
        corpus.epoch = corpus.epoch + 1

        db_session.add(corpus)
        db_session.commit()
    else:
        # generate corpus name
        source_name, _, _ = services.corpus.source_uri_parse(source_uri=source_uri)

        corpus_name = services.corpus.name_generate(
            corpus=source_name,
            prefix=os.environ.get("APP_FS_PREFIX", ""),
        )

        # create corpus
        corpus = services.corpus.create(
            db_session=db_session,
            embed_dims=services.corpus.embed_dims(model=model),
            embed_model=model,
            epoch=1,
            name=corpus_name,
            org_id=0,
            params={
                "meta": {
                    "splitter": splitter,
                }
            },
            source_uri=source_uri,
            state=models.corpus.STATE_DRAFT,
        )

    return corpus