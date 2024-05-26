import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import main_shared
import models
import services.corpus
import services.corpus.fs
import services.corpus.keyword
import services.corpus.vector
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

@app.get("/rag")
def rag_home():
    return fastapi.responses.RedirectResponse("/rag/corpuses")


@app.get("/rag/corpus", response_class=fastapi.responses.HTMLResponse)
def corpus_list(
    request: fastapi.Request,
    query: str = "",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if "HX-Request" in request.headers:
        htmx_request = 1
    else:
        htmx_request = 0

    logger.info(f"{context.rid_get()} rag corpus htmx {htmx_request} query '{query}'")

    try:
        list_result = services.corpus.list(db_session=db_session, query=query, offset=0, limit=50)
        corpus_list = list_result.objects
        query_code = 0
        query_result = f"{list_result.total} results"
    except Exception as e:
        corpus_list = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} rag corpus query exception '{e}'")

    if htmx_request == 1:
        template = "rag/corpus/list_table.html"
    else:
        template = "rag/corpus/list.html"

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

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response


@app.get("/rag/ingest", response_class=fastapi.responses.HTMLResponse)
async def corpus_ingest(
    background_tasks: fastapi.BackgroundTasks,
    corpus_id: int=0,
    source_uri: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    try:
        corpus = services.corpus.init(
            db_session=db_session,
            corpus_id=corpus_id,
            source_uri=source_uri,
            model=services.corpus.utils.MODEL_NAME_DEFAULT,
            splitter=services.corpus.utils.SPLITTER_NAME_DEFAULT,
        )

        logger.info(f"{context.rid_get()} rag ingest corpus '{corpus.name}' id {corpus.id}")

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
        logger.error(f"{context.rid_get()} rag ingest exception '{e}'")
        return fastapi.responses.RedirectResponse("/rag/fs")

    return fastapi.responses.RedirectResponse(f"/rag/corpus/{corpus.id}")


@app.get("/rag/query", response_class=fastapi.responses.HTMLResponse)
def corpus_query(
    request: fastapi.Request,
    corpus: str = "",  # full corpus name
    mode: str = "retrieve",
    query: str = "",
    limit: int = 10,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    list_result = services.corpus.list(db_session=db_session, query="", offset=0, limit=10)
    corpus_list = [object.name for object in list_result.objects]

    modes = ["augment", "keyword", "retrieve"]
    models = services.corpus.embed_models()

    query_nodes = []
    query_response = ""
    query_ok = ""
    query_error = ""

    if corpus and query:
        logger.info(f"{context.rid_get()} rag retrieve corpus '{corpus}' mode '{mode}' query '{query}'")

        try:
            if mode == "augment":
                augment_result = services.corpus.vector.search_augment(
                    db_session=db_session,
                    name_encoded=corpus,
                    query=query,
                )

                if augment_result.code != 0:
                    query_error = f"error: {augment_result.errors[0]}"
                else:
                    query_response = augment_result.response
                    query_ok = f"response in {round(augment_result.msec, 0)} msec"
            elif mode == "retrieve":
                retrieve_result = services.corpus.vector.search_retrieve(
                    db_session=db_session,
                    name_encoded=corpus,
                    query=query,
                    limit=limit,
                )

                if retrieve_result.code != 0:
                    query_error = f"error: {retrieve_result.errors[0]}"
                else:
                    query_nodes = retrieve_result.nodes
                    query_ok = f"{len(query_nodes)} results in {round(retrieve_result.msec, 0)} msec"

                    # todo
                    # services.corpus.text_ratios(texts=[node.text for node in nodes])
            elif mode == "keyword":
                retrieve_result = services.corpus.keyword.search_retrieve(
                    db_session=db_session,
                    name_encoded=corpus,
                    query=query,
                    limit=limit,
                )

                if retrieve_result.code != 0:
                    query_error = f"error: {retrieve_result.errors[0]}"
                else:
                    query_nodes = retrieve_result.nodes
                    query_ok = f"{len(query_nodes)} results in {round(retrieve_result.msec, 0)} msec"

        except Exception as e:
            query_error = f"exception: {e}"
            logger.error(f"{context.rid_get()} rag retrieve exception '{e}'")

    else:
        logger.info(f"{context.rid_get()} rag retrieve index")

    return templates.TemplateResponse(
        request,
        "rag/corpus/query.html",
        {
            "app_name": "Rag",
            "app_version": app_version,
            "corpus": corpus,
            "corpus_list": corpus_list,
            "mode": mode,
            "models": models,
            "modes": modes,
            "prompt_text": "ask a question",
            "query": query,
            "query_error": query_error,
            "query_ok": query_ok,
            "query_nodes": query_nodes,
            "query_response": query_response,
        }
    )


@app.get("/rag/corpus/{corpus_id}", response_class=fastapi.responses.HTMLResponse)
def corpus_show(request: fastapi.Request, corpus_id: int, db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    """
    """
    logger.info(f"{context.rid_get()} rag corpus show {corpus_id}")

    try:
        corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)
    except Exception as e:
        logger.error(f"{context.rid_get()} rag corpus show exception '{e}'")

    return templates.TemplateResponse(
        request,
        "rag/corpus/show.html",
        {
            "app_name": "Corpus",
            "app_version": app_version,
            "corpus": corpus,
        }
    )


@app.get("/rag/fs", response_class=fastapi.responses.HTMLResponse)
def fs_list(
    request: fastapi.Request,
    query: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if "HX-Request" in request.headers:
        htmx_request = 1
    else:
        htmx_request = 0

    logger.info(f"{context.rid_get()} rag fs htmx {htmx_request} query '{query}'")

    try:
        list_result = services.corpus.fs.list(
            db_session=db_session,
            local_dir=os.environ.get("APP_FS_ROOT"),
            query=query,
            offset=0,
            limit=50,
        )
        corpus_map = list_result.corpus_map
        source_uris = list_result.source_uris
        query_code = 0
        query_result = f"{len(source_uris)} results"
    except Exception as e:
        corpus_map = {}
        source_uris = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} rag fs exception '{e}'")

    if htmx_request == 1:
        template = "rag/fs/list_table.html"
    else:
        template = "rag/fs/list.html"

    response = templates.TemplateResponse(
        request,
        template,
        {
            "app_name": "Files",
            "app_version": app_version,
            "corpus_map": corpus_map,
            "query": query,
            "prompt_text": "search",
            "source_uris": source_uris,
            "query_code": query_code,
            "query_result": query_result,
        }
    )

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response
