from contextlib import contextmanager
from dataclasses import dataclass

import pymysql

from app.config import settings
from app.exceptions import DatabaseConnectionError
from app.logger import logger


@dataclass(slots=True)
class Database:
    connection: pymysql.Connection
    cursor: pymysql.cursors.DictCursor


@contextmanager
def get_database():

    connection = None
    cursor = None

    try:

        connection = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

        cursor = connection.cursor()

        logger.info("Connected to MySQL database.")

        yield Database(
            connection=connection,
            cursor=cursor,
        )

        connection.commit()

    except Exception as error:

        if connection:
            connection.rollback()

        logger.exception(error)

        raise DatabaseConnectionError(str(error))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

        logger.info("Database connection closed.")