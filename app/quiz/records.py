import datetime
import abc
from bson.objectid import ObjectId
from pymongo.database import Database
import requests
import base64
from app.libs.types import UnchangedTypedPropert, MongoIdList
import random


class MongoRecordAdapter(abc.ABC):
    """
    Abstract MongoDB record adapter
    Attributes
    ----------
    _id : bson.objectid.ObjectId
        id of MongoDB record
    db : pymongo.database.Database
        MongoDB Database reference
    Methods
    -------
    save_to_db(col)
        Save Record in MongoDB collection
    to_json()
        Abstract method for MongoRecordAdapter to json/bson converting

    """
    _id = UnchangedTypedPropert(ObjectId)
    db = UnchangedTypedPropert(Database)

    def __init__(self, db) -> None:
        """
        Set immutable Database reference
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing adapting record
        """
        self.db = db

    def save_to_db(self, col):
        """
        Save Record in MongoDB collection
        Parameters
        ----------
        col : str
            Target collection name

        Raises
        ------
        AttributeError
            Try to create new record with same params as existed one
        """
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
        """
        Abstract method for MongoRecordAdapter to json/bson converting
        """


class Game(MongoRecordAdapter):
    """
        Game style MongoDB record adapter
    Attributes
    ----------
    winner : ObjectId
        Winner of current game
    game_time : datetime.datetime
        Date and time of game starting

    Methods
    -------
    users()
    load_by_id(cls, db, games_col='games', users_col='users', guestions_col='questions')
        Alternative constructor of existed record's object selected by id
    load_from_db(col)
        Filling object params with values from existed record
    load_by_users
        Alternative constructor of existed record's object selected by users list
    save_to_db(col)
        Save Record in MongoDB collection
    to_json()
        Game to json/bson converting
    """
    winner = UnchangedTypedPropert(ObjectId)
    game_time = UnchangedTypedPropert(datetime.datetime)

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        """
        Create initial Game style record
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing Game style record
        games_col : str, default 'games'
            Games collection name
        users_col : str, default 'users'
            Users collection name
        guestions_col : str, default 'questions'
            Questions collection name
        """
        super().__init__(db)
        self._users = MongoIdList()
        self._users.set_collection(self.db[users_col])
        self.questions = []
        self.score = []
        self.is_finished = False

    @property
    def users(self):
        """
            Property of users' list
        Returns
        -------
        MongoIdList
            Set og unique ObjectIds
        """
        return self._users

    @classmethod
    def load_by_id(cls, db, _id, games_col='games', users_col='users', guestions_col='questions'):
        """
            Alternative constructor of existed record's object selected by id
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing Game style record
        _id : ObjectId
            Id of loaded record
        games_col : str, default 'games'
            Games collection name
        users_col : str, default 'users'
            Users collection name
        guestions_col : str, default 'questions'
            Questions collection name

        Returns
        -------
        Game
            New instance of Game class containing values of existed record
        """
        instance = cls(db, games_col, users_col, guestions_col)
        instance._id = _id
        instance.load_from_db(games_col)
        return instance

    def load_from_db(self, col):
        """
            Filling object params with values from existed record
        Parameters
        ----------
        col : str
            Name of games collection

        Raises
        ------
        TODO Check all pymongo Exceptions
        """
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
        """
            Alternative constructor of existed record's object selected by users list
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing Game style record
        users : MongoIdList
            List of users ObjectIds
        col : str
            Name of games collection

        Returns
        -------
        Game
            New instance of Game class containing values of existed record
        """
        result = list(db[col].find(
            {'users': {'$all': users}}))   # Find query to find only identic users' list
        for game in result:
            if set(result[0]['users']) == set(users):
                return cls.load_by_id(db, result[0]['_id'])
        else:
            return None

    def save_to_db(self, col):
        """
            Save Record in MongoDB collection
        Parameters
        ----------
        col : str
            Name of games collection
        """
        try:
            self.game_time = datetime.datetime.now()
        except AttributeError:
            print('Game saved again')
        super().save_to_db(col)

    def to_json(self):
        """
            Game to json/bson converting
        Returns
        -------
        dict
            Json format object params
        """
        return {'date': self.game_time, 'users': list(self.users), 'questions': self.questions, 'winner': self.winner, 'is_finished': self.is_finished, 'score': self.score}


class User(MongoRecordAdapter):
    """
        User style MongoDB record adapter
    Attributes
    ----------
    name : str
        User's name
    game_time : datetime.datetime
        Date and time of game starting

     Methods
    -------
    games()
    load_by_id(cls, db, games_col='games', users_col='users', guestions_col='questions')
        Alternative constructor of existed record's object selected by id
    load_from_db(col)
        Filling object params with values from existed record
    load_by_name
        Alternative constructor of existed record's object selected by user's name
    save_to_db(col)
        Save Record in MongoDB collection
    to_json()
        Game to json/bson converting
    """
    name = UnchangedTypedPropert(str, '')

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        """
        Create initial User style record
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing User style record
        games_col : str, default 'games'
            Games collection name
        users_col : str, default 'users'
            Users collection name
        guestions_col : str, default 'questions'
            Questions collection name

        """
        super().__init__(db)
        self._games = MongoIdList()
        self._games.set_collection(self.db[games_col])
        self.questions = []
        self.correct_answers = 0

    @property
    def games(self):
        """
            Property of games' list
        Returns
        -------
        MongoIdList
            Set of unique ObjectIds
        """
        return self._games

    @classmethod
    def load_by_id(cls, db, _id, games_col='games', users_col='users', guestions_col='questions'):
        """
            Alternative constructor of existed record's object selected by id

        Parameters
        ----------
        db : pymongo.database.Database
            Database containing User style record
        _id : ObjectId
            Id of loaded record
        games_col : str, default 'games'
            Games collection name
        users_col : str, default 'users'
            Users collection name
        guestions_col : str, default 'questions'
            Questions collection name

        Returns
        -------
        User
            New instance of User class containing values of existed record
        """
        instance = cls(db, games_col, users_col, guestions_col)
        instance._id = _id
        instance.load_from_db(users_col)
        return instance

    def load_from_db(self, col):
        """
            Filling object params with values from existed record
        Parameters
        ----------
        col : str
            Name of users collection

        Raises
        ------
        TODO Check all pymongo Exceptions
        """
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
        """
            User to json/bson converting
        Returns
        -------
        dict
            Json format object params
        """
        return {'name': self.name, 'correct_answers': self.correct_answers, 'questions': self.questions, 'games': list(self.games)}

    @classmethod
    def load_by_name(cls, db, name, col):
        """
            Alternative constructor of existed record's object selected by user's name
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing User style record
        name : str
            User's name
        col : str
            Name of users collection

        Returns
        -------
        User
            New instance of User class containing values of existed record
        """
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
    """
        Question style MongoDB record adapter
    Attributes
    ----------
    category : str
        Category of question
    question : str
        Text of question
    correct_answer : str
        Text of correct answers
    incorrect_answers : list of str
        List of incorrect answers
    question_code : str
        8 characters code of question used for question recognizing
     Methods
    -------
    load_by_id(cls, db, games_col='games', users_col='users', guestions_col='questions')
        Alternative constructor of existed record's object selected by id
    load_from_db(col)
        Filling object params with values from existed record
    load_new_question()
        Trivia API request for geting new random question
    get_unknown_question(cls, db, questions, col)
        Alternative constructor for record containing question not contained in list
    save_to_db(col)
        Save Record in MongoDB collection
    to_json()
        Game to json/bson converting
    """
    category = UnchangedTypedPropert(str, '')
    question = UnchangedTypedPropert(str, '')
    correct_answer = UnchangedTypedPropert(str, '')
    incorrect_answers = UnchangedTypedPropert(list, [])
    question_code = UnchangedTypedPropert(str, '')

    def __init__(self, db, games_col='games', users_col='users', guestions_col='questions') -> None:
        """
        Create initial Question style record
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing Question style record
        games_col : str, default 'games'
            Games collection name
        users_col : str, default 'users'
            Users collection name
        guestions_col : str, default 'questions'
            Questions collection name
        """
        super().__init__(db)

    @classmethod
    def load_by_id(cls, db, _id, games_col='games', users_col='users', guestions_col='questions'):
        """
            Alternative constructor of existed record's object selected by id

        Parameters
        ----------
        db : pymongo.database.Database
            Database containing Question style record
        _id : ObjectId
            Id of loaded record
        games_col : str, default 'games'
            Games collection name
        users_col : str, default 'users'
            Users collection name
        guestions_col : str, default 'questions'
            Questions collection name

        Returns
        -------
        Question
            New instance of Question class containing values of existed record
        """
        instance = cls(db, games_col, users_col, guestions_col)
        instance._id = _id
        instance.load_from_db(guestions_col)
        return instance

    def load_from_db(self, col):
        """
            Filling object params with values from existed record
        Parameters
        ----------
        col : str
            Name of questions collection

        Raises
        ------
        TODO Check all pymongo Exceptions
        """
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
        """
            Question to json/bson converting
        Returns
        -------
        dict
            Json format object params
        """
        return {'question': self.question, 'category': self.category, 'correct_answer': self.correct_answer, 'incorrect_answers': self.incorrect_answers, 'question_code': self.question_code}

    def load_new_question(self):
        """
            load_new_question
        """
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
        """
            Alternative constructor for record containing question not contained in list
        Parameters
        ----------
        db : pymongo.database.Database
            Database containing Question style record
        questions : list of str
            Known questions list
        col : str
            Name of questions collection

        Returns
        -------
        Question
            Unique new instance of Question class
        """
        result = list(db[col].find(
            {"question_code": {'$nin': questions}}))
        try:
            random_question = random.choice(result)
        except Exception as e:
            print('EEEEE', e)
            new_question = cls(db)
            # TODO check if new receiving question is not in list
            new_question.load_new_question()
            new_question.save_to_db(col)
        else:
            new_question = cls.load_by_id(db, random_question['_id'])
        finally:
            return new_question

    def __str__(self) -> str:
        """
            Present Question object in string
        Returns
        -------
        str
            Question string format
        """
        return self.question_code
