from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from core.database import Base
from core.config import (
    AISHORASUB_DATABASE_URL,
    MEERALINKS_DATABASE_URL,
    HZQUICKLINK_DATABASE_URL,
)

from models.users import *
from models.admin import *
from models.plans.network import *
from models.plans.cable import *
from models.plans.disco import *
from models.plans.bulk_sms import *
from models.plans.exam import *


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


DATABASE_URLS = {
    "aishorasub": AISHORASUB_DATABASE_URL,
    "meeralinks": MEERALINKS_DATABASE_URL,
    "hzquicklink": HZQUICKLINK_DATABASE_URL,
}


db_name = context.get_x_argument(
    as_dictionary=True
).get("db")

if db_name not in DATABASE_URLS:
    raise ValueError(
        "Specify a valid database with -x db=<name>"
    )


database_url = DATABASE_URLS[db_name]

config.set_main_option(
    "sqlalchemy.url",
    database_url
)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()