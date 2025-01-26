#!/usr/bin/env python3
from application import Application
from database import database
from migrations.migrate import upgrade


if __name__ in ("__main__", "__mp_main__"):
    upgrade(database)
    app = Application()
    app.run()
