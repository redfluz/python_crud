from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    age: int

@dataclass
class UserInput:
    name: str
    age: str