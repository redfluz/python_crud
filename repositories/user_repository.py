from config.connection import Database
from models.user_model import User


class UserRepository:

    def __init__(self, database: Database):
        self._database = database

    def find_all(self) -> list[User]:
        with self._database.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, age FROM users ORDER BY id")
                return [User(id=r[0], name=r[1], age=r[2]) for r in cursor.fetchall()]

    def find_by_id(self, user_id: int) -> User | None:
        with self._database.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, age FROM users WHERE id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                return User(id=row[0], name=row[1], age=row[2]) if row else None

    def create(self, user: User) -> bool:
        with self._database.connect() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (name, age) VALUES (%s, %s)",
                        (user.name, user.age),
                    )
                    user.id = cursor.lastrowid  # populate id in place
                connection.commit()
                return True
            except Exception:
                connection.rollback()
                return False

    def update(self, user: User) -> bool:
        with self._database.connect() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET name = %s, age = %s WHERE id = %s",
                        (user.name, user.age, user.id),
                    )
                    rowcount = cursor.rowcount
                connection.commit()
                return rowcount > 0
            except Exception:
                connection.rollback()
                return False

    def delete(self, user: User) -> bool:
        with self._database.connect() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM users WHERE id = %s", (user.id,))
                    rowcount = cursor.rowcount
                connection.commit()
                return rowcount > 0
            except Exception:
                connection.rollback()
                return False
