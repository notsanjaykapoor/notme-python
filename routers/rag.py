import os

import fastapi
import sqlmodel

import context
import log
import main_shared
import services.corpus

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers/rag")

app = fastapi.APIRouter(
    tags=["app.rag"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]

@app.get("/rag/corpuses", response_class=fastapi.responses.HTMLResponse)
def rag_corpuses(request: fastapi.Request, db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    """
    """
    list_result = services.corpus.list_(db_session=db_session, query="", offset=0, limit=50)
    corpus_list = list_result.objects

    print(corpus_list)

    return templates.TemplateResponse(
        request,
        "corpuses.html",
        {
            "app_name": "Corpuses",
            "app_version": app_version,
            "corpus_list": corpus_list,
        }
    )


@app.get("/rag/query", response_class=fastapi.responses.HTMLResponse)
def rag_query(
    request: fastapi.Request,
    collection: str = "",
    mode: str = "retrieve",
    query: str = "",
    limit: int = 10,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    list_result = services.corpus.list_(db_session=db_session, query="", offset=0, limit=10)
    collections = [object.name for object in list_result.objects]

    modes = ["augment", "keyword", "retrieve"]
    models = services.corpus.embed_models()

    query_nodes = []
    query_response = ""
    query_ok = ""
    query_error = ""

    if collection and query:
        logger.info(f"{context.rid_get()} rag retrieve collection '{collection}' mode '{mode}' query '{query}'")

        try:
            if mode == "augment":
                augment_result = services.corpus.vector_search_augment(
                    db_session=db_session,
                    name_encoded=collection,
                    query=query,
                )

                if augment_result.code != 0:
                    query_error = f"error: {augment_result.errors[0]}"
                else:
                    query_response = augment_result.response
                    query_ok = f"response generated in {round(augment_result.msec, 0)} msec"
            elif mode == "retrieve":
                retrieve_result = services.corpus.vector_search_retrieve(
                    db_session=db_session,
                    name_encoded=collection,
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
                retrieve_result = services.corpus.keyword_search_retrieve(
                    db_session=db_session,
                    name_encoded=collection,
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
    else:
        logger.info(f"{context.rid_get()} rag retrieve index")

    return templates.TemplateResponse(
        request,
        "query.html",
        {
            "app_name": "Rag",
            "app_version": app_version,
            "collection": collection,
            "collections": collections,
            "mode": mode,
            "models": models,
            "modes": modes,
            "prompt_text": "ask a question",
            "query_error": query_error,
            "query_ok": query_ok,
            "query_nodes": query_nodes,
            "query_response": query_response,
            "query": query,
        }
    )
