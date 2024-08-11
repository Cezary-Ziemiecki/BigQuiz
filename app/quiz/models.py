from app.quiz.records import User, Question, Game
import random
from pymongo.database import Database
from app.libs.types import UnchangedTypedPropert
from collections import OrderedDict


class Quiz:
    """
    Quiz manager based on MongoDB

    Attributes
    ----------
    db : pymongo.database.Database
        MongoDB Database reference

    Methods
    -------
    loaded_users()
        List of User MongoDB Records
    current_question()
    current_question(question)
        Set new question and reset MongoDB state for new answers
    start_game(game)
        Set new or saved Game and load it's state
    update_game(game)
        Update game and users params in connected MongoDB records
    consider_question()
        Check if all answers for current question are received and in that case edit game and users params
    register_user(user)
        Add user ro loaded users list and prepare game state for additional one
    get_known_questions()
        Prepare unique question codes list based on users questions
    register_answer(user_name,choice)
        Put choice in user's key update answers order and run loading new question if needed 
    load_next_question()
        Load new question based on previous one
    propose_game()
        Check if in games collection is unfinished game started by all loaded users
    """
    db = UnchangedTypedPropert(Database)

    def __init__(self, db):
        """
            Initialize quiz game manager with default state
        Parameters
        ----------
        db : pymongo.database.Database
            MongoDB Database reference
        """
        self.db = db
        self._loaded_users = OrderedDict()
        self._current_question = None
        self._shuffled_answers = [0, 1, 2, 3]
        self._users_answers = OrderedDict()
        self._score = OrderedDict()
        self._order = []
        self.__current_game = None

    @property
    def loaded_users(self):
        """
            List of User MongoDB Records
        Returns
        -------
        list of User
            Values of loaded users dictionary
        """
        return self._loaded_users.values()

    @property
    def current_question(self):
        """_summary_
            Get current loaded question
        Returns
        -------
        Question
            Current loaded question
        """
        return self._current_question

    @current_question.setter
    def current_question(self, question):
        """
            Set new question and reset MongoDB state for new answers
        Parameters
        ----------
        question : Question
            New Question element to load as current
        """
        if isinstance(question, Question):
            self._users_answers = dict.fromkeys(self._users_answers, None)
            self._order = []
            self._current_question = question
            random.shuffle(self._shuffled_answers)

    def start_game(self, game):
        """
            Set Game and load it's state
        Parameters
        ----------
        game : Game
            New or saved Game object
        """
        if isinstance(game, Game):
            self.__current_game = game
            if game._id == None:
                for user in self.loaded_users:
                    game.users.append(user._id)
                game.save_to_db('games')
                for user in self.loaded_users:
                    user.games.append(game._id)
                self._score = OrderedDict.fromkeys(self._score, 0)
            else:
                self._score = OrderedDict(
                    [(k, v) for k, v in zip(self._score.keys(), game.score)])
            self.load_next_question()

    def update_game(self):
        """
            Update game and users params in connected MongoDB records
        """
        self.__current_game.save_to_db('games')
        for user in self.loaded_users:
            user.save_to_db('users')

    def consider_question(self):
        """
            Check if all answers for current question are received and in that case edit game and users params
        Returns
        -------
        Boolean
            Completeness of the question
        """
        if all([answer is not None for answer in self._users_answers.values()]):
            for user, answer in self._users_answers.items():
                if not self._shuffled_answers[answer]:
                    self._score[user] += 1
                    self._loaded_users[user].correct_answers += 1
                self._loaded_users[user].questions.append(
                    self.current_question.question_code)
            return True
        return False

    def register_user(self, user):
        """
            Add user ro loaded users list and prepare game state for additional one
        Parameters
        ----------
        user : User
            New user taking part in QuizGame

        Raises
        ------
        TypeError
            New user is not in User type
        """
        if isinstance(user, User):
            self._users_answers[user.name] = None
            self._score[user.name] = 0
            self._loaded_users[user.name] = user
        else:
            raise TypeError

    def get_known_questions(self):
        """_summary_
            Prepare unique question codes list based on users questions
        Returns
        -------
        list
            Question codes
        """
        known_questions_codes = set()
        for user in self.loaded_users:
            for question in user.questions:
                known_questions_codes.add(question)
        return list(known_questions_codes)

    def register_answer(self, user_name, choice):
        """
            Put choice in user's key update answers order and run loading new question if needed 
        Parameters
        ----------
        user_name : str
            Name of responded user
        choice : int
            Id of given answer

        Returns
        -------
        Boolean
            Saving state of given answer

        TODO EXCEPTIONS
        """
        if self.__current_game:
            try:
                self._users_answers[user_name] = choice
            except KeyError:
                print('Unregistered user')
            else:
                try:
                    self._order.remove(user_name)
                except ValueError:
                    print('This user answer first time')
                finally:
                    self._order.append(user_name)
                if self.consider_question():
                    self.__current_game.questions.append(
                        self.current_question.question_code)
                    self.__current_game.score = list(self._score.values())
                    self.update_game()
                    self.load_next_question()
                return True
        return False

    def load_next_question(self):
        """
            Load new question based on previous one
        """
        self.current_question = Question.get_unknown_question(
            self.db, self.get_known_questions(), 'questions')

    def propose_game(self):
        """
            Check if in games collection is unfinished game started by all loaded users
        Returns
        -------
        Game
            Game record reference connected with all users
        """
        proposed_game = Game.load_by_users(
            self.db, [x._id for x in self.loaded_users], 'games')
        return proposed_game or Game(self.db)
