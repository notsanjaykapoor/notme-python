import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
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


@app.get("/admin/fs", response_class=fastapi.responses.HTMLResponse)
def admin_fs_list(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=50,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} admin fs query '{query}'")

    if "HX-Request" in request.headers:
        htmx_request = 1
    else:
        htmx_request = 0

    try:
        list_result = services.corpus.fs.dirs(
            db_session=db_session,
            local_dir=os.environ.get("APP_FS_ROOT"),
            query=query,
            offset=offset,
            limit=limit,
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
        logger.error(f"{context.rid_get()} admin fs exception '{e}'")

    if htmx_request == 1:
        template = "admin/fs/list_table.html"
    else:
        template = "admin/fs/list.html"

    try:
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
    except Exception as e:
        logger.error(f"{context.rid_get()} admin fs render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response
