import dataclasses

import sqlmodel

import models
import services.corpus
import services.corpus.fs

@dataclasses.dataclass
class Struct:
    code: int
    dirty_objects: list
    scan_count: int
    errors: list[str]


def scan(db_session: sqlmodel.Session, mode: str) -> Struct:
    """
    Scan corpus files that have changed and optionally mark them as dirty
    """
    struct = Struct(
        code=0,
        dirty_objects = [],
        scan_count = 0,
        errors =[],
    )

    # get corpus list

    list_result = services.corpus.list(
        db_session=db_session,
        query="",
        offset=0,
        limit=1024,
    )

    # scan each corpus for changes

    for corpus in list_result.objects:
        _, source_host, _ = services.corpus.fs.source_uri_parse(source_uri=corpus.source_uri)

        if source_host == "localhost":
            local_files = services.corpus.fs.files_path_list(source_uri=corpus.source_uri, filter="")

            fingerprint = services.corpus.fs.files_fingerprint(files=local_files)

            struct.scan_count += 1

            if corpus.fingerprint != fingerprint:
                if mode == "update":
                    corpus.state = models.corpus.STATE_DIRTY
                    db_session.add(corpus)
                    db_session.commit()

                struct.dirty_objects.append(corpus)
        else:
            continue # host not supported

    return struct
