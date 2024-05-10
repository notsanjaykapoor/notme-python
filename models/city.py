import geoalchemy2
import shapely.geometry
import sqlalchemy
import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()


class City(Base):  # type: ignore
    """use sqlalchemy orm instead of sqlmodel"""

    __tablename__ = "cities"

    class Config:
        arbitrary_types_allowed = True

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    loc = sqlalchemy.Column(geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    def pack(self):
        return {
            "id": self.id,
            "loc": self.loc,
            "name": self.name,
        }

    @property
    def point(self) -> shapely.geometry.Point:
        return shapely.wkb.loads(bytes(self.loc.data))
