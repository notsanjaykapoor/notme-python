import pydantic_factories

import models


class EntityFactory(pydantic_factories.ModelFactory):
    __model__ = models.Entity
