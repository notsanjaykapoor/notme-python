import json

import neo4j
import sqlmodel
import toml  # type: ignore

import services.cities
import services.data_links
import services.data_mappings
import services.data_models
import services.database
import services.entity_watches
import services.graph.commands
import services.graph.indexes
import services.graph.session


def reset(db: sqlmodel.Session, neo: neo4j.Session, config_path: str = "./data/notme/config"):
    """
    reset database:
      1. migrate database
      3. truncate all database tables
      3. initialize database config data
    """
    services.database.session.migrate()

    reset_graph(neo)
    reset_db(db)
    reset_db_config(db=db, config_path=config_path)


def reset_db(db: sqlmodel.Session):
    services.database.truncate_all(db=db)


def reset_db_config(db: sqlmodel.Session, config_path: str = "./data/notme/config"):
    toml_dict = toml.load(f"{config_path}/cities.toml")
    services.cities.Create(db=db, objects=toml_dict["cities"]).call()

    services.data_models.Slurp(db=db, toml_file=f"{config_path}/data_models.toml").call()
    services.data_links.Slurp(db=db, toml_file=f"{config_path}/data_links.toml").call()
    services.entity_watches.Slurp(db=db, toml_file=f"{config_path}/entity_watches.toml").call()

    json_objects = json.load(open(f"{config_path}/data_mappings.json"))
    services.data_mappings.Create(db=db, objects=json_objects).call()


def reset_graph(neo: neo4j.Session):
    services.graph.commands.truncate(neo)
    services.graph.indexes.create(neo)
