import logging
import os

import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class MySQLConnection:
    def __init__(self, db):
        self.connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def query_db(self, query, data=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, data or {})
                if query.lstrip().lower().startswith(("select", "show")):
                    return cursor.fetchall()
                if query.lstrip().lower().startswith("insert"):
                    return cursor.lastrowid
                return cursor.rowcount
        except Exception:
            logger.exception("Error al ejecutar una consulta MySQL")
            raise
        finally:
            self.connection.close()


def connectToMySQL(db):
    return MySQLConnection(db)
