import json
import os
from app.quiz.records import User


class Quiz:
    def __init__(self):
        self._loaded_users = []

    @property
    def loaded_users(self):
        return self._loaded_users

    def register_user(self, user):
        if isinstance(user, User):
            self._loaded_users.append(user)
        else:
            raise TypeError
