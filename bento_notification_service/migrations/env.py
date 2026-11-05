import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from bento_notification_service.config import get_config
from bento_notification_service.models import Base

config = context.config

fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# The database location comes from the service configuration, not from alembic.ini. Allow an explicit override
# (e.g., from tests) via the `sqlalchemy.url` main option.
db_url = config.get_main_option("sqlalchemy.url") or get_config().database_url
target_metadata = Base.metadata


def run_migrations_offline():
    """
    Run migrations in 'offline' mode: configure the context with just a URL (no Engine), emitting SQL to the script
    output.
    """
    context.configure(url=db_url, target_metadata=target_metadata, literal_binds=True, render_as_batch=True)

    with context.begin_transaction():
        context.run_migrations()


def _process_revision_directives(_context, _revision, directives):
    # Prevent an auto-migration from being generated when there are no changes to the schema
    if getattr(config.cmd_opts, "autogenerate", False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            logger.info("No changes in schema detected.")


def _do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=_process_revision_directives,
        render_as_batch=True,  # required for ALTER TABLE support in SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


async def _run_async_migrations():
    connectable = create_async_engine(db_url)

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """
    Run migrations in 'online' mode: create an async Engine and associate a connection with the context.
    """
    asyncio.run(_run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
