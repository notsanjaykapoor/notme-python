import os
import time
import traceback

import fastapi
import fastapi.responses
import llama_cpp
import sqlmodel

import context
import log
import main_shared
import services.corpus
import services.corpus.fs
import services.corpus.llm
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


@app.get("/corpus/{corpus_id}/query", response_class=fastapi.responses.HTMLResponse)
def corpus_query(
    request: fastapi.Request,
    corpus_id: int,
    mode: str = "retrieve",
    query: str = "",
    limit: int = 10,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    corpus = services.corpus.get_by_id(db_session=db_session, id=corpus_id)

    list_result = services.corpus.list(db_session=db_session, query=f"id:{corpus.id}", offset=0, limit=10)
    corpus_list = list_result.objects

    modes = [
        "retrieve",
        "answer",
    ]

    query_nodes = []
    query_response = ""
    query_ok = ""
    query_error = ""

    try:
        if query:
            logger.info(f"{context.rid_get()} corpus '{corpus.name}' model '{corpus.model_name}' {mode} query '{query}'")

            if mode in ["answer"]:
                search_result = services.corpus.vector.search(
                    corpus=corpus,
                    query=query,
                    limit=2, # use a small number here
                )

                llm_scope = "\n".join(node.text for node in search_result.nodes)

                t_start = time.time()

                llm = llama_cpp.Llama(
                    model_path=os.environ.get("APP_LLM_PATH"),
                    n_ctx=2048,
                    verbose=False,
                )

                llm_response = llm(
                    services.corpus.llm.prompt(scope=llm_scope, query=query),
                    max_tokens=None, # set to None to generate up to the end of the context window
                    stop=["Q:", "\n"], # stop generating just before the model would generate a new question
                    temperature=0.1,
                )

                t_end = time.time()

                logger.info(f"{context.rid_get()} corpus '{corpus.name}' model '{corpus.model_name}' {mode} response {llm_response}")

                query_ok = f"llm response in {round(t_end - t_start, 2)}s"
                query_response = llm_response.get("choices")[0].get("text").strip()
            elif mode in ["retrieve"]:
                search_result = services.corpus.vector.search(
                    corpus=corpus,
                    query=query,
                    limit=limit,
                )

                if search_result.code != 0:
                    query_error = f"error: {search_result.errors[0]}"
                else:
                    query_nodes = search_result.nodes
                    query_ok = f"{len(query_nodes)} results in {round(search_result.msec, 0)}ms"

                    logger.info(f"{context.rid_get()} corpus '{corpus.name}' model '{corpus.model_name}' {mode} response - {len(query_nodes)} results")
        else:
            logger.info(f"{context.rid_get()} corpus retrieve index")
    except Exception as e:
        query_error = f"exception: {e}"
        logger.error(f"{context.rid_get()} corpus '{corpus}' query exception '{e}' - '{traceback.format_exc()}'")

    if "HX-Request" in request.headers:
        html_template = "rag/query_fragment.html"
    else:
        html_template = "rag/query.html"

    try:
        response = templates.TemplateResponse(
            request,
            html_template,
            {
                "app_name": "Corpus Rag",
                "app_version": app_version,
                "corpus": corpus,
                "corpus_list": corpus_list,
                "mode": mode,
                "modes": modes,
                "query": query,
                "query_error": query_error,
                "query_ok": query_ok,
                "query_nodes": query_nodes,
                "query_prompt": "ask a question",
                "query_response": query_response,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} rag retrieve render exception '{e}' - '{traceback.format_exc()}'")

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?mode={mode}&query={query}"

    return response