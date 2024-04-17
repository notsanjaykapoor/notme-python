import fastapi

import context
import log
import os
import main_shared

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers/me")

app = fastapi.APIRouter(
    tags=["app.me"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/me", response_class=fastapi.responses.HTMLResponse)
def me(request: fastapi.Request):
    logger.info(f"{context.rid_get()} me")

    version = os.environ["APP_VERSION"]
    return templates.TemplateResponse(request, "me.html", {"app_version": version})
