import fastapi

import log  # noqa: E402
import main_shared

app = fastapi.APIRouter(
    tags=["app.health"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

# kubernetes inspired health probes
@app.get("/health")
@app.get("/health/live")
@app.get("/health/ready")
@app.get("/health/startup")
def api_health():
    return {
        "api": "up",
    }


@app.get("/ping")
def api_ping():
    return {
        "code": 0,
        "message": "pong",
    }
