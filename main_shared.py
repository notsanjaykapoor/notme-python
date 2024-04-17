import fastapi

import services.database.session


# sync db dependency
def get_db():
    with services.database.session.get() as session:
        yield session


# async db dependency (e.g. gql)
async def get_gql_context(db=fastapi.Depends(get_db)):
    return {"db": db}
