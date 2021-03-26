from databases import Database
from os import environ


DB_USER = environ.get('DB_USER', 'root')
DB_PASSWORD = environ.get('DB_PASSWORD', 'root')
DB_HOST = environ.get('DB_HOST', 'localhost')
DB_NAME = environ.get('DB_NAME', 'sweet_delivery')
DB_PORT = environ.get('DB_PORT', '5442')

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
database = Database(DATABASE_URL)