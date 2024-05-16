import sqlmodel

import models
import services.milvus


def delete_by_name(db_session: sqlmodel.Session, name: str) -> int:
    """
    Delete corpus object from milvus and postgres dbs
    """
    milvus_code = services.milvus.delete_by_name(collection=name)

    if milvus_code not in [0, 404]:
        return milvus_code

    # its possible that postgres object exists even if milvus object doesn't

    model = models.Corpus
    dataset = sqlmodel.select(model)

    dataset = dataset.where(model.collection_name == name)
    object = db_session.exec(dataset).first()

    if not object:
        if milvus_code == 404:
            return 404
        else:
            return 0 # milvus object was deleted, postgres doesn't  exist

    db_session.delete(object)
    db_session.commit()

    return 0



