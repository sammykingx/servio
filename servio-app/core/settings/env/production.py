import os
from decouple import config
import pymysql


# pymysql.install_as_MySQLdb()



DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(", ")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": "3306",
        "CONN_MAX_AGE": 120,
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
            "isolation_level": "read committed",
        },
    }
}
