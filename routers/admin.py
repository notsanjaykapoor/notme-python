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
def admin_workq(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=20,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} admin workq query '{query}'")

    try:
        list_result = services.work_queue.list(db_session=db_session, query=query, offset=offset, limit=limit)
        work_objects = list_result.objects
    except Exception as e:
        work_objects = []
        logger.error(f"{context.rid_get()} admin workq exception '{e}'")

    return templates.TemplateResponse(
        request,
        "admin/workq_list.html",
        {
            "app_name": "WorkQ",
            "app_version": app_version,
            "prompt_text": "search",
            "query": query,
            "work_objects": work_objects,
        }
    )
