import datetime
import abc
import collections.abc as collections
from bson.objectid import ObjectId
from pymongo.errors import InvalidName
from pymongo.database import Database
import requests
import base64


class UnchangedProperty(abc.ABC):
    def __init__(self, default=None) -> None:
        self.instances = {}
        self._default = default

    def __get__(self, instance, parent):
        if instance is None:
            return self
        try:
            return self.instances[instance]
        except KeyError:
            return self._default
        except Exception as e:
            print(e)

    def __set__(self, instance, value):
        if instance in self.instances:
            raise AttributeError("can't set attribute")
        else:
            try:
                value = self.validate(value)
            except Exception as e:
                print(e)
            else:
                self.instances[instance] = value

    @abc.abstractmethod
    def validate(self, value):
        """"""


class UnchangedTypedPropert(UnchangedProperty):

    def __init__(self, cls, default=None) -> None:
        super().__init__(default)
        self._cls = cls

    def validate(self, value):
        if isinstance(value, self._cls):
            return value
        else:
            raise TypeError


class IterableStorage(abc.ABC):

    def __init__(self):
        self.storage = []

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __setitem__(self, key, value):
        try:
            value = self.validate(value)
        except Exception as e:
            print(e)
        else:
            self.storage[key] = value

    def __iter__(self):
        return iter(self.storage)

    def __getitem__(self, index):
        return self.storage[index]

    def append(self, value):
        try:
            value = self.validate(value)
        except Exception as e:
            print(e)
        else:
            print(self.storage, value)
            self.storage.append(value)

    @abc.abstractmethod
    def validate(self, value):
        """"""


class MongoId():
    def __init__(self, collection):
        super().__init__()
        self.collection = collection

    def validate(self, value):
        print(f'waliduje: {value}')
        if type(value) == ObjectId:
            result = self.collection.find({'_id': value})
        elif type(value) in [str, int]:
            object_id = ['0']*(24-len(str(value)))+list(str(value))
            value = ObjectId(''.join(object_id))
            result = self.collection.find(
                {'_id': ObjectId(''.join(object_id))})
        else:
            raise ValueError('value must be in type ObjectId, str or int')
        if len(list(result)):
            if not isinstance(self, collections.Iterable) or value not in list(self):
                return value
            raise ValueError(f'Value {value} is in collection')
        raise InvalidName(f'There was no record with id: {value}')


class MongoIdList(MongoId, IterableStorage):
    """"""


class Game:
    _id = UnchangedTypedPropert(ObjectId)
    db = UnchangedTypedPropert(Database)
    winner = UnchangedTypedPropert(ObjectId)
    game_time = UnchangedTypedPropert(datetime.time)

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        self.db = db
        self.users = MongoIdList(self.db[users_col])
        self.questions = []
        self.is_finished = False
        self.successes = []

    @classmethod
    def load_by_id(cls, db, _id, games_col='games', users_col='users', guestions_col='questions'):
        instance = cls(db, games_col, users_col, guestions_col)
        instance._id = _id
        instance.load_from_db(games_col)
        return instance

    def load_from_db(self, col):
        try:
            result = self.db[col].find({'_id': self._id})[0]
        except Exception as e:
            raise e
        else:
            self.is_finished = result['is_finished']
            for user in result['users']:
                self.users.append(user)
            if result['winner'] != self.winner:
                self.winner = result['winner']
            self.questions = result['questions']
            self.successes = result['successes']


class User:
    _id = UnchangedTypedPropert(ObjectId)
    db = UnchangedTypedPropert(Database)

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        self.db = db
        self.games = MongoIdList(self.db[games_col])
        self.questions = []
        self.correct_answers = 0

    @classmethod
    def load_by_id(cls, db, _id, games_col='games', users_col='users', guestions_col='questions'):
        instance = cls(db, games_col, users_col, guestions_col)
        instance._id = _id
        instance.load_from_db(users_col)
        return instance

    def load_from_db(self, col):
        try:
            result = self.db[col].find({'_id': self._id})[0]
        except Exception as e:
            raise e
        else:
            for game in result['games']:
                self.games.append(game)
            self.questions = result['questions']
            self.correct_answers = result['correct_answers']


class Question:
    _id = UnchangedTypedPropert(ObjectId)
    db = UnchangedTypedPropert(Database)
    category = UnchangedTypedPropert(str, '')
    question = UnchangedTypedPropert(str, '')
    correct_answer = UnchangedTypedPropert(str, '')
    incorrect_answers = UnchangedTypedPropert(list, [])
    question_code = UnchangedTypedPropert(str, '')

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        self.db = db

    @classmethod
    def load_by_id(cls, db, _id, games_col='games', users_col='users', guestions_col='questions'):
        instance = cls(db, games_col, users_col, guestions_col)
        instance._id = _id
        instance.load_from_db(guestions_col)
        return instance

    def load_from_db(self, col):
        try:
            result = self.db[col].find({'_id': self._id})[0]
        except Exception as e:
            raise e
        else:
            self.question = result['question']
            self.category = result['category']
            self.correct_answer = result['correct_answer']
            self.incorrect_answers = result['incorrect_answers']
            self.question_code = result['question_code']

    def save_to_db(self, col):
        x = self.db[col].insert_one(self.to_json())
        self._id = ObjectId(x.inserted_id)

    def to_json(self):
        return {'question': self.question, 'category': self.category, 'correct_answer': self.correct_answer, 'incorrect_answers': self.incorrect_answers, 'question_code': self.question_code}

    def load_new_question(self):
        api_url = "https://opentdb.com/api.php?amount=1&category=17&difficulty=easy&type=multiple"
        response = requests.get(api_url).json()['results'][0]
        self.category = response['category']
        self.question = response['question']
        self.correct_answer = response['correct_answer']
        self.incorrect_answers = response['incorrect_answers']
        coded = base64.b64encode(response['question'].encode()).decode()
        self.question_code = coded[:2]+coded[-5:-2]
