import os
import traceback

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import main_shared
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
    return fastapi.responses.RedirectResponse("/rag/query")


@app.get("/rag/query", response_class=fastapi.responses.HTMLResponse)
def rag_query(
    request: fastapi.Request,
    corpus_name: str = "",  # full corpus name
    mode: str = "retrieve",
    query: str = "",
    limit: int = 10,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    list_result = services.corpus.list(db_session=db_session, query="", offset=0, limit=10)
    corpus_list = [object.name for object in list_result.objects]

    modes = [
        "augment",
        # "keyword",
        "retrieve",
    ]

    query_nodes = []
    query_response = ""
    query_ok = ""
    query_error = ""

    if corpus_name and query:
        corpus = services.corpus.get_by_name(db_session=db_session, name=corpus_name)

        logger.info(f"{context.rid_get()} corpus '{corpus.name}' model '{corpus.model_name}' {mode} query '{query}'")

        try:
            if mode == "augment":
                augment_result = services.corpus.vector.search_augment(
                    db_session=db_session,
                    corpus=corpus,
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
                    corpus=corpus,
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
                    corpus=corpus,
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
            logger.error(f"{context.rid_get()} corpus '{corpus}' retrieve exception '{e}' - '{traceback.format_exc()}'")

    else:
        logger.info(f"{context.rid_get()} corpus retrieve index")

    try:
        response = templates.TemplateResponse(
            request,
            "rag/query.html",
            {
                "app_name": "Rag",
                "app_version": app_version,
                "corpus_name": corpus_name,
                "corpus_list": corpus_list,
                "mode": mode,
                "modes": modes,
                "prompt_text": "ask a question",
                "query": query,
                "query_error": query_error,
                "query_ok": query_ok,
                "query_nodes": query_nodes,
                "query_response": query_response,
            }
        )

        return response
    except Exception as e:
        logger.error(f"{context.rid_get()} rag retrieve render exception '{e}' - '{traceback.format_exc()}'")
