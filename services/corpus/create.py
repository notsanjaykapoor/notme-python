import datetime

import sqlmodel

import models


def create(
    db_session: sqlmodel.Session,
    name: str,
    embed_model: str,
    embed_dims: int,
    epoch: int,
    org_id: int,
    source_uri: str,
    state: str,
    params: dict,
) -> models.Corpus:
    """
    Create database corpus object.
    """
    corpus = models.Corpus(
        docs_count=params.get("docs_count") or 0,
        embed_dims=embed_dims,
        embed_model=embed_model,
        epoch=epoch,
        files_count=params.get("files_count") or 0,
        meta=params.get("meta") or {},
        name=name,
        nodes_count=params.get("nodes_count") or 0,
        org_id=org_id,
        signature=params.get("signature") or "",
        source_uri=source_uri,
        state=state,
        updated_at=datetime.datetime.now(datetime.timezone.utc)
    )

    db_session.add(corpus)
    db_session.commit()

    return corpus