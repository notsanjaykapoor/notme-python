import hashlib
import json

import models

EXCLUDE_COLUMNS = ["fingerprint", "id", "tags", "version"]


def fingerprint_entities(entities: list[models.Entity]) -> str:
    # get entity table columns, filter out columns not used for fingerprint
    column_names = [c.name for c in models.Entity.__table__.columns if c.name not in EXCLUDE_COLUMNS]

    # sort entities first, then sort entity keys
    entities = sorted(entities, key=lambda o: (o.slug, o.type_value))
    objects = list(map(lambda o: {name: str(getattr(o, name)) for name in column_names}, entities))
    objects_str = json.dumps(objects, sort_keys=True)

    return hashlib.md5(objects_str.encode("utf-8")).hexdigest()
