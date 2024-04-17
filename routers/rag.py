import fastapi

import context
import log
import main_shared
import os
import services.corpus

import langchain_community
import langchain_community.embeddings

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers/rag")

app = fastapi.APIRouter(
    tags=["app.rag"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/rag/{corpus}/query", response_class=fastapi.responses.HTMLResponse)
def rag_query(requst: fastapi.Request, corpus: str, query: str):
    logger.info(f"{context.rid_get()} rag corpus '{corpus}' query '{query}'")

    db_name = f"faiss/{corpus}"
    embedding = langchain_community.embeddings.GPT4AllEmbeddings()

    agent_result = services.corpus.chat_agent(db_name=db_name, embedding=embedding, prompt_name="hwchase17/openai-tools-agent")
    agent_executor = agent_result.agent_executor

    result = agent_executor.invoke({"input": query})
    answer = result.get("output")

    logger.info(f"{context.rid_get()} rag corpus '{corpus}' response")

    return answer


@app.get("/rag", response_class=fastapi.responses.HTMLResponse)
@app.get("/rag/{corpus}", response_class=fastapi.responses.HTMLResponse)
def rag(request: fastapi.Request):
    corpus = request.path_params.get("corpus", "")
    version = os.environ["APP_VERSION"]

    logger.info(f"{context.rid_get()} rag corpus '{corpus}'")

    search_result = services.corpus.search(query="")
    corpus_names = search_result.names
 
    if corpus and corpus not in corpus_names:
        return fastapi.responses.RedirectResponse("/rag")

    if corpus:
        app_name = f"Corpus '{corpus}'"
        prompt_text = "ask a question"
    else:
        app_name = "Rag"
        prompt_text = "select a corpus"

    return templates.TemplateResponse(
        request,
        "rag.html",
        {
            "app_name": app_name,
            "app_version": version,
            "corpus_name": corpus,
            "prompt_text": prompt_text,
        }
    )
