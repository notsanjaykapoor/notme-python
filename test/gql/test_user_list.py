import random

import pytest
import sqlmodel
import strawberry
from strawberry.schema.config import StrawberryConfig

import gql
import services.users

gql_schema = strawberry.Schema(
    query=gql.Query,
    config=StrawberryConfig(auto_camel_case=False),
)


@pytest.fixture()
def user_id(session: sqlmodel.Session):
    user_id = f"user-{random.randint(1,100)}"
    struct_create = services.users.Create(db=session, user_id=user_id).call()
    assert struct_create.code == 0
    assert struct_create.id

    yield user_id

    services.users.delete_by_id(db=session, ids=[struct_create.id])


def test_gql_user_list(session: sqlmodel.Session, user_id: str):
    query = """
        query TestQuery($query: String, $offset: Int, $limit: Int) {
            users_list(query: $query, offset: $offset, limit: $limit) {
                code
                objects {
                    user_id
                }
            }
        }
    """

    result = gql_schema.execute_sync(
        query,
        variable_values={"query": ""},
        context_value={"db": session},
    )

    print(f"result {result}")

    assert result.errors is None

    data = result.data["users_list"]

    assert data["code"] == 0
    assert len(data["objects"]) == 1
    assert data["objects"][0]["user_id"] == user_id
