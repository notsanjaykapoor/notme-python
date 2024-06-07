import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import models
import main_shared
import services.work_queue

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app.rag"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]


@app.get("/admin/corpus/ingest", response_class=fastapi.responses.HTMLResponse)
async def admin_corpus_ingest(
    request: fastapi.Request,
    corpus_id: int=0,
    source_uri: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    try:
        if corpus_id:
            corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)
        else:
            corpus = services.corpus.get_by_source_uri(db_session=db_session, source_uri=source_uri)

        if not corpus:
            corpus = services.corpus.create(
                db_session=db_session,
                epoch=0,
                model=services.corpus.utils.MODEL_NAME_DEFAULT,
                org_id=0,
                params={
                    "meta": {
                        "splitter": services.corpus.utils.SPLITTER_NAME_DEFAULT,
                    }
                },
                source_uri=source_uri,
                state=models.corpus.STATE_DRAFT,
            )

        logger.info(f"{context.rid_get()} admin corpus {corpus.id} name '{corpus.name}' ingest")

        corpus.epoch += 1
        corpus.state = models.corpus.STATE_QUEUED
        db_session.add(corpus)
        db_session.commit()

        services.work_queue.add(
            db_session=db_session,
            data={
                "corpus_id": corpus.id
            },
            msg="ingest",
            queue=models.work_queue.QUEUE_CORPUS_INGEST,
            partition=services.work_queue.partition(
                buckets=models.work_queue.QUEUE_CORPUS_INGEST_PARTITIONS,
                id=corpus.id,
            ),
        )

        # background_tasks.add_task(
        #     services.corpus.ingest,
        #     db_session=db_session,
        #     corpus_id=corpus.id
        # )
    except Exception as e:
        logger.error(f"{context.rid_get()} admin corpus ingest exception '{e}'")
        return fastapi.responses.RedirectResponse(request.headers.get("referer"))

    return fastapi.responses.RedirectResponse(f"/admin/corpus?query={corpus.name}")


@app.get("/admin/corpus", response_class=fastapi.responses.HTMLResponse)
def admin_corpus_list(
    request: fastapi.Request,
    query: str = "",
    offset: int=0,
    limit: int=50,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if "HX-Request" in request.headers:
        htmx_request = 1
    else:
        htmx_request = 0

    logger.info(f"{context.rid_get()} admin corpus query '{query}'")

    try:
        list_result = services.corpus.list(
            db_session=db_session,
            query=query,
            offset=offset,
            limit=limit,
        )
        corpus_list = list_result.objects
        query_code = 0
        query_result = f"query '{query}' returned {list_result.total} results"
    except Exception as e:
        corpus_list = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} admin corpus query exception '{e}'")

    if htmx_request == 1:
        template = "admin/corpus/list_table.html"
    else:
        template = "admin/corpus/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Corpus",
                "app_version": app_version,
                "corpus_list": corpus_list,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} admin corpus list render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response


@app.get("/admin/corpus/{corpus_id}", response_class=fastapi.responses.HTMLResponse)
def admin_corpus_show(request: fastapi.Request, corpus_id: int, db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    """
    """
    logger.info(f"{context.rid_get()} admin corpus show {corpus_id}")

    try:
        corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)
    except Exception as e:
        logger.error(f"{context.rid_get()} admin corpus show exception '{e}'")

    response = templates.TemplateResponse(
        request,
        "admin/corpus/show.html",
        {
            "app_name": "Corpus",
            "app_version": app_version,
            "corpus": corpus,
        }
    )

    return response


@app.get("/admin/corpus/{corpus_id}/files", response_class=fastapi.responses.HTMLResponse)
def admin_corpus_files(
    request: fastapi.Request,
    corpus_id: int,
    source_uri: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} corpus {corpus_id} source '{source_uri}' files")

    try:
        corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)

        source_uri = source_uri or corpus.source_uri

        files_result = services.corpus.fs.files(
            source_uri=source_uri,
            filter="",
        )
        files_list = files_result.files_list
        files_map = files_result.files_map
    except Exception as e:
        logger.error(f"{context.rid_get()} corpus {corpus_id} files exception '{e}'")

    try:
        response = templates.TemplateResponse(
            request,
            "admin/corpus/files.html",
            {
                "app_name": "Corpus",
                "app_version": app_version,
                "corpus": corpus,
                "files_list": files_list,
                "files_map": files_map,
                "source_uri": source_uri,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} corpus {corpus_id} files render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
