import pytest
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from .records import User, Game, Question
from pymongo.database import Database

thing = {'users': None}


@pytest.fixture
def example_game():
    pass


def test_create_game():
    # TODO find good Mongo Database Mock or use normal MongoClient
    assert True
