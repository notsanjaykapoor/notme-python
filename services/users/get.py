from sqlmodel import select, Session

from sqlmodel.sql.expression import Select, SelectOfScalar
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

from models.user import User

class Get:
  def __init__(self, db: Session, user_id: str):
    self.db = db
    self.user_id = user_id

  def call(self):
    return self.db.exec(select(User).where(User.user_id == self.user_id)).first()
