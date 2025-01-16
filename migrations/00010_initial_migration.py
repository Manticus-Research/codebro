import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Session, Message, ContextPath


def upgrade(database):
    database.create_tables([Session, Message, ContextPath])


def downgrade(database):
    database.drop_tables([Session, Message, ContextPath])
