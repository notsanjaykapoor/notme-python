import geoalchemy2
import shapely.geometry
import sqlalchemy

Base = sqlalchemy.ext.declarative.declarative_base()


class EntityLocation(Base):  # type: ignore
    """sqlalchemy orm instead of sqlmodel"""

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

    @property
    def point(self) -> shapely.geometry.Point:
        return shapely.wkb.loads(bytes(self.loc.data))
