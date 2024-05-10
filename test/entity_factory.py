import factory.alchemy

import models

class EntityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Entity
        sqlalchemy_session_persistence = "commit"

    entity_key = "entity_key"
    entity_name = "entity_name"
    fingerprint = "fingerprint"
    name = "name"
    node = 0
    slug = "slug"
    state = "state"
    type_name = "type_name"
    version = "1"
