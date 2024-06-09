import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import models
import main_shared
import services.work_queue

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]

@app.get("/admin")
def admin_home():
    return fastapi.responses.RedirectResponse("/admin/corpus")
