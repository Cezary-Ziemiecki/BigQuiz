from libs.types import UnchangedTypedPropert, MongoIdList
from .records import User, Game, Question


class Quiz():
    def __init__(self) -> None:
        self._current_game
