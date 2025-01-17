from database import Session, Message, ContextPath


def upgrade(database):
    database.create_tables([Session, Message, ContextPath])


def downgrade(database):
    database.drop_tables([Session, Message, ContextPath])
