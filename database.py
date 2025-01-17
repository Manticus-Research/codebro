from datetime import datetime, timezone

from peewee import (
    Model,
    SqliteDatabase,
    TextField,
    DateTimeField,
    ForeignKeyField,
)

database = SqliteDatabase("codebuddy.db")


class BaseModel(Model):
    class Meta:
        database = database


class Session(BaseModel):
    name = TextField(index=True)
    working_dir = TextField(index=True)
    started_at = DateTimeField(default=datetime.now(timezone.utc))
    last_message_at = DateTimeField(default=datetime.now(timezone.utc))


class ContextPath(BaseModel):
    path = TextField()
    session = ForeignKeyField(Session, backref="context_paths")


class Message(BaseModel):
    session = ForeignKeyField(Session, backref="messages")
    model = TextField(index=True)
    role = TextField(index=True)
    content = TextField()
    full_message = TextField()
    timestamp = DateTimeField(default=datetime.now(timezone.utc))
