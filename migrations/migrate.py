import os
import re
from datetime import datetime, timezone
from peewee import Model, TextField, DateTimeField


def ensure_migration_table(db):
    class Migration(Model):
        name = TextField()
        applied_at = DateTimeField(default=datetime.now(timezone.utc))

        class Meta:
            database = db

    db.create_tables([Migration], safe=True)
    return Migration


def upgrade(database):
    """Apply all new migrations."""
    Migration = ensure_migration_table(database)

    # Check for migration files in the migrations directory.
    migration_files = os.listdir(os.path.dirname(__file__))
    migration_file_pattern = re.compile(r"^\d{5}_.+\.py$")
    migration_files = sorted(
        [f for f in migration_files if migration_file_pattern.match(f)]
    )

    # Get the last migration that was applied.
    last_migration = Migration.select().order_by(Migration.applied_at.desc()).first()
    last_migration_name = last_migration.name if last_migration else None

    # Apply any new migrations.
    applied_migrations = []
    for migration_file in migration_files:
        if last_migration_name is None or migration_file > last_migration_name:
            migration_module = __import__(
                f"migrations.{migration_file[:-3]}", fromlist=["upgrade"]
            )
            with database.atomic():
                migration_module.upgrade(database)
                Migration.create(name=migration_file)
            applied_migrations.append(migration_file)
            print(f"Applied migration: {migration_file}")

    if applied_migrations:
        print("All migrations applied.")


def downgrade(database):
    """Revert the latest migration."""
    Migration = ensure_migration_table(database)

    last_migration = Migration.select().order_by(Migration.applied_at.desc()).first()
    if last_migration:
        migration_module = __import__(
            f"migrations.{last_migration.name[:-3]}", fromlist=["downgrade"]
        )
        with database.atomic():
            migration_module.downgrade(database)
            last_migration.delete_instance()
        print(f"Reverted migration: {last_migration.name}")
    else:
        print("No migrations to revert.")
