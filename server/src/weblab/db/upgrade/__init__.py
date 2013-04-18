from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.environment import EnvironmentContext
from alembic import command

from sqlalchemy import create_engine

URL = 'sqlite:///foo.db'
ALEMBIC_PATH = 'alembic'

def get_config():
    config = Config("alembic.ini")
    config.set_main_option("script_location", ALEMBIC_PATH)
    config.set_main_option("url", URL)
    config.set_main_option("sqlalchemy.url", URL)
    return config

def is_head():
    engine = create_engine(URL)

    script = ScriptDirectory.from_config(get_config())
    current_head = script.get_current_head()

    context = MigrationContext.configure(engine)
    current_rev = context.get_current_revision()

    return current_head == current_rev

def upgrade():
    command.upgrade(get_config(), "head")

if __name__ == '__main__':
    if is_head():
        print "Already in head"
    else:
        upgrade()
