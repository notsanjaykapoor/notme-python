import fastapi

import context
import log
import main_shared
import os
import services.corpus

import langchain.chains
import langchain_openai.chat_models
import langchain_community
import langchain_community.embeddings
import langchain_community.vectorstores
from langchain import hub

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers/rag")

app = fastapi.APIRouter(
    tags=["app.rag"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.post("/rag/corpus", response_class=fastapi.responses.RedirectResponse)
async def rag_corpus(request: fastapi.Request):
    bytes = await request.body()
    value = bytes.decode("utf-8").split("=")[1]

    rag_llm = request.cookies.get("rag_llm") or "local"

    logger.info(f"{context.rid_get()} rag llm '{rag_llm}' corpus '{value}'")

    response = fastapi.responses.RedirectResponse(f"/rag/{value}")
    response.status_code = 302

    return response


@app.post("/rag/llm", response_class=fastapi.responses.RedirectResponse)
async def rag_llm(request: fastapi.Request):
    bytes = await request.body()
    value = bytes.decode("utf-8").split("=")[1]

    logger.info(f"{context.rid_get()} rag llm '{value}'")

    response = fastapi.responses.RedirectResponse("/rag")
    response.set_cookie(key="rag_llm", value=value, secure=False)
    response.status_code = 302

    return response


@app.get("/rag/{corpus}/query", response_class=fastapi.responses.HTMLResponse)
def rag_query(request: fastapi.Request, corpus: str, query: str):
    rag_llm = request.cookies.get("rag_llm") or "local"

    logger.info(f"{context.rid_get()} rag corpus '{corpus}' llm '{rag_llm}' query '{query}'")

    db_name = f"faiss/{corpus}"
    embedding = langchain_community.embeddings.GPT4AllEmbeddings()

    db = langchain_community.vectorstores.FAISS.load_local(db_name, embedding, allow_dangerous_deserialization=True)

    if rag_llm == "local":
        llm = langchain_community.llms.GPT4All(model=os.environ["RAG_MODEL_PATH"], callbacks=[], verbose=True)
        chain_result = services.corpus.qa_chain(db=db, llm=llm)
        chain = chain_result.chain

        result = chain({"question": query, "chat_history": []})
        answer = result.get("answer")
    else:
        prompt = hub.pull("hwchase17/openai-tools-agent")
        llm = langchain_openai.chat_models.ChatOpenAI(temperature = 0)

        agent_result = services.corpus.chat_agent(db=db, llm=llm, prompt=prompt)
        agent_executor = agent_result.agent_executor

        result = agent_executor.invoke({"input": query})
        answer = result.get("output")

    logger.info(f"{context.rid_get()} rag corpus '{corpus}' response")

    return answer

@app.get("/rag", response_class=fastapi.responses.HTMLResponse)
@app.get("/rag/{corpus}", response_class=fastapi.responses.HTMLResponse)
def rag(request: fastapi.Request):
    corpus = request.path_params.get("corpus", "")
    rag_llm = request.cookies.get("rag_llm") or "local"
    version = os.environ["APP_VERSION"]

    rag_llms = ["local", "openai"]

    logger.info(f"{context.rid_get()} rag llm '{rag_llm}' corpus '{corpus}'")

    search_result = services.corpus.search(query="")
    corpus_names = search_result.names
 
    if corpus and corpus not in corpus_names:
        return fastapi.responses.RedirectResponse("/rag")

    if corpus:
        app_name = f"Rag corpus '{corpus}'"
        prompt_text = "ask a question"
    else:
        app_name = f"Rag"
        corpus_names = ["select a corpus"] + corpus_names
        prompt_text = ""

    return templates.TemplateResponse(
        request,
        "rag.html",
        {
            "app_name": app_name,
            "app_version": version,
            "corpus_name": corpus,
            "corpus_names": corpus_names,
            "prompt_text": prompt_text,
            "rag_llm": rag_llm,
            "rag_llms": rag_llms,
        }
    )
