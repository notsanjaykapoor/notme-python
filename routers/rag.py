import fastapi

import context
import log
import main_shared
import os
import services.corpus
import starlette.responses

import langchain.retrievers.document_compressors
import langchain_openai.chat_models
import langchain_community
import langchain_community.embeddings
import langchain_community.llms
import langchain_community.vectorstores
from langchain import hub
import phoenix
import phoenix.trace.langchain

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers/rag")

app = fastapi.APIRouter(
    tags=["app.rag"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]


@app.post("/rag/corpus", response_class=fastapi.responses.RedirectResponse)
async def rag_corpus(request: fastapi.Request):
    """
    Select a corpus (deprecated)
    """
    bytes = await request.body()
    value = bytes.decode("utf-8").split("=")[1]

    rag_llm = request.cookies.get("rag_llm") or "local"

    logger.info(f"{context.rid_get()} rag llm '{rag_llm}' corpus '{value}'")

    response = fastapi.responses.RedirectResponse(f"/rag/{value}")
    response.status_code = 302

    return response


@app.post("/rag/llm", response_class=fastapi.responses.RedirectResponse)
async def rag_llm(request: fastapi.Request):
    """
    Select a llm (deprecated)
    """
    bytes = await request.body()
    value = bytes.decode("utf-8").split("=")[1]

    logger.info(f"{context.rid_get()} rag llm '{value}'")

    response = fastapi.responses.RedirectResponse("/rag")
    response.set_cookie(key="rag_llm", value=value, secure=False)
    response.status_code = 302

    return response


@app.get("/rag/query", response_class=fastapi.responses.HTMLResponse)
def rag_query(request: fastapi.Request, corpus_name: str, retriever_type: str, query: str):
    logger.info(f"{context.rid_get()} rag corpus '{corpus_name}' retriever '{retriever_type}' query '{query}'")

    db_url = os.environ.get("DATABASE_VECTOR_URL")

    list_result = services.corpus.list_all(db_url=db_url)
    corpus_names = list_result.names

    retriever_types = ["basic", "compress"]

    retrieve_result = services.corpus.retrieve(db_url=db_url, db_name=corpus_name, retriever_type=retriever_type, query=query)
    docs = retrieve_result.docs

    print(docs)

    # return starlette.responses.JSONResponse(texts)

    return templates.TemplateResponse(
        request,
        "rag.html",
        {
            "app_name": "Rag Example",
            "app_version": app_version,
            "corpus_name": corpus_name,
            "corpus_names": corpus_names,
            "docs": docs,
            "prompt_text": "ask a question",
            "query": query,
            "retriever_types": retriever_types,
        }
    )


@app.get("/rag", response_class=fastapi.responses.HTMLResponse)
def rag(request: fastapi.Request):
    db_url = os.environ.get("DATABASE_VECTOR_URL")

    list_result = services.corpus.list_all(db_url=db_url)
    corpus_names = list_result.names

    retriever_types = ["basic", "compress"]

    logger.info(f"{context.rid_get()} rag")

    return templates.TemplateResponse(
        request,
        "rag.html",
        {
            "app_name": "Rag Example",
            "app_version": app_version,
            "corpus_name": "",
            "corpus_names": corpus_names,
            "docs": [],
            "prompt_text": "ask a question",
            "query": "",
            "retriever_types": retriever_types,
        }
    )
