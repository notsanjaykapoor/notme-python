import geoalchemy2
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EntityLocation(Base):  # type: ignore
    """use sqlalchemy orm instead of sqlmodel"""

    __tablename__ = "entity_locations"

    class Config:
        arbitrary_types_allowed = True

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    entity_id = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    loc = sqlalchemy.Column(geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=False)

    def pack(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "loc": self.loc,
        }
