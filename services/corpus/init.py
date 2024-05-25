import models
import sqlmodel

import services.corpus


def init(db_session: sqlmodel.Session, source_uri: str, model: str, splitter: str) -> models.Corpus:
    """
    
    """
    corpus = services.corpus.get_by_source_uri(db_session=db_session, source_uri=source_uri)

    if corpus:
        # update corpus
        corpus.epoch = corpus.epoch + 1

        db_session.add(corpus)
        db_session.commit()
    else:
        # generate corpus name
        source_name, _, _, _ = services.corpus.source_uri_parse(source_uri=source_uri)
        corpus_name = services.corpus.name_encode(corpus=source_name, model=model, splitter=splitter)

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