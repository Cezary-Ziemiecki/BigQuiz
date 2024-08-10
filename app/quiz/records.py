import datetime
import abc
from bson.objectid import ObjectId
from pymongo.database import Database
import requests
import base64
from app.libs.types import UnchangedTypedPropert, MongoIdList
import random


class MongoRecordAdapter(abc.ABC):
    _id = UnchangedTypedPropert(ObjectId)
    db = UnchangedTypedPropert(Database)

    def __init__(self, db) -> None:
        self.db = db

    def save_to_db(self, col):
        new_record = self.to_json()
        result = self.db[col].find(new_record)
        if self._id == None:
            if not len(list(result)):
                x = self.db[col].insert_one(new_record)
                self._id = ObjectId(x.inserted_id)
            else:
                raise AttributeError
        else:
            self.db[col].update_one({'_id': self._id},  {
                '$set': new_record})

    @abc.abstractmethod
    def to_json(self):
        """"""


class Game(MongoRecordAdapter):
    winner = UnchangedTypedPropert(ObjectId)
    game_time = UnchangedTypedPropert(datetime.datetime)

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        super().__init__(db)
        self._users = MongoIdList()
        self._users.set_collection(self.db[users_col])
        self.questions = []
        self.score = []
        self.is_finished = False

    @property
    def users(self):
        return self._users

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
            self.score = result['score']

    @classmethod
    def load_by_users(cls, db, users, col):
        result = list(db[col].find(
            {'users': {'$all': users}}))   # Find query to find only identic users list
        for game in result:
            if set(result[0]['users']) == set(users):
                return cls.load_by_id(db, result[0]['_id'])
        else:
            return False

    def save_to_db(self, col):
        try:
            self.game_time = datetime.datetime.now()
        except AttributeError:
            print('Game saved again')
        return super().save_to_db(col)

    def to_json(self):
        return {'date': self.game_time, 'users': list(self.users), 'questions': self.questions, 'winner': self.winner, 'is_finished': self.is_finished, 'score': self.score}


class User(MongoRecordAdapter):
    name = UnchangedTypedPropert(str, '')

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        super().__init__(db)
        self._games = MongoIdList()
        self._games.set_collection(self.db[games_col])
        self.questions = []
        self.correct_answers = 0

    @property
    def games(self):
        return self._games

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
            self.name = result['name']
            self.questions = result['questions']
            self.correct_answers = result['correct_answers']

    def to_json(self):
        return {'name': self.name, 'correct_answers': self.correct_answers, 'questions': self.questions, 'games': list(self.games)}

    @classmethod
    def load_by_name(cls, db, name, col):
        result = list(db[col].find(
            {'name': name}))
        try:
            return cls.load_by_id(db, result[0]['_id'])
        except Exception as e:
            new_user = cls(db)
            new_user.name = name
            new_user.save_to_db(col)
            return new_user


class Question(MongoRecordAdapter):
    category = UnchangedTypedPropert(str, '')
    question = UnchangedTypedPropert(str, '')
    correct_answer = UnchangedTypedPropert(str, '')
    incorrect_answers = UnchangedTypedPropert(list, [])
    question_code = UnchangedTypedPropert(str, '')

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        super().__init__(db)

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

    def to_json(self):
        return {'question': self.question, 'category': self.category, 'correct_answer': self.correct_answer, 'incorrect_answers': self.incorrect_answers, 'question_code': self.question_code}

    def load_new_question(self):
        api_url = "https://opentdb.com/api.php?amount=1&type=multiple"
        response = requests.get(api_url).json()['results'][0]
        self.category = response['category']
        self.question = response['question']
        self.correct_answer = response['correct_answer']
        self.incorrect_answers = response['incorrect_answers']
        coded = base64.b64encode(response['question'].encode()).decode()
        self.question_code = coded[1:5]+coded[-8:-4]

    @classmethod
    def get_unknown_question(cls, db, questions, col):
        result = list(db[col].find(
            {"question_code": {'$nin': questions}}))
        try:
            random_question = random.choice(result)
        except Exception as e:
            print('EEEEE', e)
            new_question = cls(db)
            new_question.load_new_question()
            new_question.save_to_db(col)
        else:
            new_question = cls.load_by_id(db, random_question['_id'])
        finally:
            return new_question

    def __str__(self) -> str:
        return self.question_code
