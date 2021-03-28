import os

import pytest

os.environ['TESTING'] = 'True'

from alembic import command
from alembic.config import Config
from app.db import TEST_SQLALCHEMY_DATABASE_URL
from sqlalchemy_utils import create_database, drop_database


@pytest.fixture()
def temp_db():
    create_database(TEST_SQLALCHEMY_DATABASE_URL)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    db_dir = os.path.join(base_dir, "db")
    alembic_cfg = Config(os.path.join(db_dir, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(db_dir, "migrations"))
    command.upgrade(alembic_cfg, "head")

    try:
        yield TEST_SQLALCHEMY_DATABASE_URL
    finally:
        drop_database(TEST_SQLALCHEMY_DATABASE_URL)
