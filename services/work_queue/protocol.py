import typing

import sqlmodel

import models

class WorkObjectHandler(typing.Protocol):
    def call(self, db_session: sqlmodel.Session, work_object: models.WorkQueue) -> int:
        pass