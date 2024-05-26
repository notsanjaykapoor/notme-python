import models
import services.corpus.queue

from .protocol import WorkObjectHandler

handlers = {
    models.work_queue.QUEUE_CORPUS_INGEST : services.corpus.queue.CorpusIngestHandler
}


def route(queue: str) -> WorkObjectHandler | None:
    """
    """
    return handlers.get(queue)

    