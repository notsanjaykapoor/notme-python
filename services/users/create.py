from sqlmodel import select, Session

from models.user import User

class Create:

  def __init__(self, db: Session, user_id: str):
    self.db = db
    self.user_id = user_id

  def call(self):
    db_object = User(user_id=self.user_id)

    self.db.add(db_object)
    self.db.commit()

    return db_object.id
