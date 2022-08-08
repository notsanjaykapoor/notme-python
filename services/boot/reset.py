import toml  # type: ignore

import services.data_links
import services.data_models
import services.database
import services.entity_watches
import services.graph.commands
import services.graph.session


def reset(config_path: str = "./data/notme/config"):
    """
    reset database:
      1. migrate database
      3. truncate all database tables
      3. initialize database config data
    """
    services.database.session.migrate()

    with services.database.session.get() as db, services.graph.session.get() as neo:
        services.graph.commands.truncate(neo)

        services.database.truncate_all(db=db)

        toml_dict = toml.load(f"{config_path}/cities.toml")
        services.cities.Create(db=db, objects=toml_dict["cities"]).call()

        services.data_models.Slurp(db=db, toml_file=f"{config_path}/data_models.toml").call()
        services.data_links.Slurp(db=db, toml_file=f"{config_path}/data_links.toml").call()
        services.entity_watches.Slurp(db=db, toml_file=f"{config_path}/entity_watches.toml").call()
