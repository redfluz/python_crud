from models.user_model import User, UserInput


class UserService:
    def __init__(self, user_repository):
        self._repository = user_repository

    def find_all(self) -> list[User]:
        return self._repository.find_all()

    def find_by_id(self, user_id: int) -> User | None:
        return self._repository.find_by_id(user_id)

    def create(self, data: UserInput) -> bool:
        user = self._validate(data)
        return self._repository.create(user)

    def update(self, user_id: int, data: UserInput) -> bool:
        user = self._validate(data)
        user.id = user_id
        return self._repository.update(user)

    def delete(self, user_id: int) -> bool:
        user = User(id=user_id, name="", age=0)
        return self._repository.delete(user)

    @staticmethod
    def _validate(data: UserInput) -> User:
        name = (data.name or "").strip()
        if not name:
            raise ValueError("Name is required.")
        if len(name) > 100:
            raise ValueError("Name must be 100 characters or fewer.")

        try:
            age = int(data.age)
        except (TypeError, ValueError):
            raise ValueError("Age must be a whole number.")

        if age < 0 or age > 150:
            raise ValueError("Age must be between 0 and 150.")

        return User(id=0, name=name, age=age)