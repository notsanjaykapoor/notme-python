import sqlmodel
import toml  # type: ignore

import services.cities


def test_entity_create(session: sqlmodel.Session):
    toml_dict = toml.load("./data/notme/config/cities.toml")

    struct_create = services.cities.Create(db=session, objects=toml_dict["cities"]).call()

    assert struct_create.code == 0
    assert struct_create.count == 3

    services.cities.delete_by_id(db=session, ids=struct_create.ids)
