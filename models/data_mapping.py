import sqlalchemy
import sqlalchemy.ext.mutable

Base = sqlalchemy.ext.declarative.declarative_base()


class DataMapping(Base):  # type: ignore
    __tablename__ = "data_mappings"

    class Config:
        arbitrary_types_allowed = True

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    model_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    obj_mapping = sqlalchemy.Column(sqlalchemy.ext.mutable.MutableDict.as_mutable(sqlalchemy.dialects.postgresql.JSONB))
    obj_name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    obj_pks = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    @property
    def obj_pks_list(self):
        return self.obj_pks.split(",")

    def pack(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "obj_mapping": self.obj_mapping,
            "obj_name": self.obj_name,
            "obj_pks": self.obj_pks,
        }
