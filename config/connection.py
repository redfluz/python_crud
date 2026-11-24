from mysql.connector.pooling import MySQLConnectionPool

import config.setting as settings


class Database:
    """Hands out connections. The pool is an internal detail."""

    def __init__(self):
        self._pool = MySQLConnectionPool(
            pool_name="python_crud",
            pool_size=5,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
        )

    def connect(self):
        """Return a connection to use with `with`."""
        return self._pool.get_connection()
