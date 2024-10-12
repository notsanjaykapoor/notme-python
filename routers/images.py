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


@app.get("/images", response_class=fastapi.responses.HTMLResponse)
def corpus_query(
    request: fastapi.Request,
    mode: str = "image-caption",
    query: str = "",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    modes = [
        "image-caption",
    ]

    rag_image_url = ""

    query_nodes = []
    query_response = ""
    query_ok = ""
    query_error = ""

    try:
        if query:
            logger.info(f"{context.rid_get()} images '{mode}' query '{query}'")

            if mode not in ["image-caption"]:
                raise ValueError("mode invalid")

            if not query.startswith("http"):
                raise ValueError("query invalid")

            rag_image_url = query

            llm_path = os.environ.get("APP_LLM_MULTI_PATH")
            llm_name = llm_path.split("/")[-1]

            logger.info(f"{context.rid_get()} images '{mode}' llm '{llm_name}'")

            llm = llama_cpp.Llama(
                model_path=llm_path,
                n_ctx=2048,
                verbose=False,
            )

            t1 = time.time()

            llm_response = llm(
                services.corpus.llm.prompt_image_caption(image_url=rag_image_url),
                max_tokens=None, # set to None to generate up to the end of the context window
                stop=["Q:", "\n"], # stop generating just before the model would generate a new question
                temperature=0.1,
            )

            t2 = time.time()

            logger.info(f"{context.rid_get()} images '{mode}' response {llm_response}")

            query_ok = f"llm response in {round(t2 - t1, 2)}s"
            query_response = llm_response.get("choices")[0].get("text").strip()
    except Exception as e:
        query_error = f"exception: {e}"
        logger.error(f"{context.rid_get()} images '{mode}' query exception '{e}' - '{traceback.format_exc()}'")


    if "HX-Request" in request.headers:
        html_template = "rag/query_fragment.html"
    else:
        html_template = "images/index.html"

    try:
        response = templates.TemplateResponse(
            request,
            html_template,
            {
                "app_name": "Image Caption",
                "app_version": app_version,
                "mode": mode,
                "modes": modes,
                "query": query,
                "query_error": query_error,
                "query_ok": query_ok,
                "query_nodes": query_nodes,
                "query_prompt": "image url",
                "query_response": query_response,
                "rag_image_url": rag_image_url,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} rag retrieve render exception '{e}' - '{traceback.format_exc()}'")

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?mode={mode}&query={query}"

    return response