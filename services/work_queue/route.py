import models
import services.corpus

from .protocol import WorkObjectHandler

handlers = {
    models.work_queue.QUEUE_CORPUS_INGEST : services.corpus.CorpusIngestHandler
}


def route(queue: str) -> WorkObjectHandler | None:
    """
    """
    return handlers.get(queue)

    