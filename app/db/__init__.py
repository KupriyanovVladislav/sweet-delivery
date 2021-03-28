from os import environ

from databases import Database

DB_USER = environ.get('DB_USER', 'root')
DB_PASSWORD = environ.get('DB_PASSWORD', 'root')
DB_HOST = environ.get('DB_HOST', 'localhost')
DB_NAME = environ.get('DB_NAME', 'sweet_delivery')
DB_PORT = environ.get('DB_PORT', '5442')

TESTING = environ.get("TESTING", False)

if TESTING:
    DB_NAME = 'sweet_delivery_test'
    TEST_SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    database = Database(TEST_SQLALCHEMY_DATABASE_URL)
else:
    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    database = Database(DATABASE_URL)
