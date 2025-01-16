from datetime import datetime, timezone

from peewee import Model, SqliteDatabase, TextField, DateTimeField, IntegerField, ForeignKeyField

database = SqliteDatabase('codebuddy.db')

class BaseModel(Model):
    class Meta:
        database = database


class Session(BaseModel):
    name = TextField()
    working_dir = TextField()
    started_at = DateTimeField(default=datetime.now(timezone.utc))
    last_message_at = DateTimeField(default=datetime.now(timezone.utc))


class ContextPath(BaseModel):
    path = TextField()
    session = ForeignKeyField(Session, backref='context_paths')


class Message(BaseModel):
    session = ForeignKeyField(Session, backref='messages')
    model = TextField()
    role = TextField()
    content = TextField()
    full_message = TextField()
    timestamp = DateTimeField(default=datetime.now(timezone.utc))
