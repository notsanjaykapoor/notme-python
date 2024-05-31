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


@app.get("/admin/workq", response_class=fastapi.responses.HTMLResponse)
def admin_workq_list(
    request: fastapi.Request,
    query: str="",
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

    logger.info(f"{context.rid_get()} admin workq query '{query}'")

    try:
        list_result = services.work_queue.list(db_session=db_session, query=query, offset=offset, limit=limit)
        work_objects = list_result.objects
        query_code = 0
        query_result = f"query '{query}' returned {list_result.total} results"
    except Exception as e:
        work_objects = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} admin workq exception '{e}'")

    if htmx_request == 1:
        template = "admin/workq/list_table.html"
    else:
        template = "admin/workq/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "WorkQ",
                "app_version": app_version,
                "prompt_text": "search",
                "query": query,
                "work_objects": work_objects,
                "query_code": query_code,
                "query_result": query_result,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} admin workq render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if htmx_request == 1:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response
