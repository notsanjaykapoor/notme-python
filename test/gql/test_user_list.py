import pytest
import random
import strawberry

from sqlmodel import Session

from strawberry.schema.config import StrawberryConfig

import gql
import services.users

gql_schema = strawberry.Schema(
    query=gql.Query,
    config=StrawberryConfig(auto_camel_case=False),
)


@pytest.fixture()
def user_id(session: Session):
    user_id = f"user-{random.randint(1,100)}"
    struct_create = services.users.Create(db=session, user_id=user_id).call()
    assert struct_create.code == 0

    yield user_id


def test_gql_user_list(session: Session, user_id: str):
    query = """
        query TestQuery($query: String, $offset: Int, $limit: Int) {
            users_list(query: $query, offset: $offset, limit: $limit) {
                code
                users {
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
    assert len(data["users"]) == 1
    assert data["users"][0]["user_id"] == user_id
