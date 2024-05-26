import sqlmodel

import models
import services.corpus


class CorpusIngestHandler:
    def call(db_session: sqlmodel.Session, work_object: models.WorkQueue) -> int:
        """
        Called in the context of a work queue worker to process a work object.
        """
        services.corpus.ingest(db_session=db_session, corpus_id=work_object.data.get("corpus_id"))

        return 0