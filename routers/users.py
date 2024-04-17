import fastapi
import sqlmodel

import context  # noqa: E402
import log  # noqa: E402
import main_shared
import models
import services.users

logger = log.init("api")


app = fastapi.APIRouter(
    tags=["app.users"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.post("/api/v1/users", response_model=int)
def user_create(user_id: str, db: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    logger.info(f"{context.rid_get()} api.users.create")

    struct = services.users.Create(db, user_id, params={}).call()

    return struct.id


@app.get("/api/v1/users/{user_id}", response_model=models.User)
def user_get(user_id: str, db: sqlmodel.Session = fastapi.Depends(main_shared.get_db)):
    logger.info(f"{context.rid_get()} api.users.get")

    struct = services.users.Get(db, user_id).call()

    return struct.user


@app.get("/api/v1/users", response_model=list[models.User])
def users_list(
    query: str = "",
    offset: int = 0,
    limit: int = 100,
    db: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} api.users.list")

    struct = services.users.List(db, query, offset, limit).call()

    logger.info(f"{context.rid_get()} api.users.list results {len(struct.objects)}")

    return struct.objects
