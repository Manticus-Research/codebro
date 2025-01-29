from datetime import datetime, timezone

from peewee import (
    Model,
    SqliteDatabase,
    TextField,
    DateTimeField,
    ForeignKeyField,
)
from playhouse.sqlite_ext import AutoIncrementField

database = SqliteDatabase("codebuddy.db")


class BaseModel(Model):
    class Meta:
        database = database


class Session(BaseModel):
    id = AutoIncrementField()
    name = TextField(index=True)
    working_dir = TextField(index=True)
    started_at = DateTimeField(default=datetime.now(timezone.utc))
    last_message_at = DateTimeField(default=datetime.now(timezone.utc))


class ContextPath(BaseModel):
    id = AutoIncrementField()
    path = TextField()
    session = ForeignKeyField(Session, backref="context_paths", on_delete="CASCADE")


class Message(BaseModel):
    id = AutoIncrementField()
    session = ForeignKeyField(Session, backref="messages", on_delete="CASCADE")
    model = TextField(index=True)
    role = TextField(index=True)
    content = TextField()
    full_message = TextField()
    timestamp = DateTimeField(default=datetime.now(timezone.utc))
