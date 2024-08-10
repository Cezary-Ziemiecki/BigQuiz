from app.quiz.records import User, Question, Game
import random
from pymongo.database import Database
from app.libs.types import UnchangedTypedPropert
from collections import OrderedDict


class Quiz:
    db = UnchangedTypedPropert(Database)

    def __init__(self, db):
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
        return self._loaded_users.values()

    @property
    def current_question(self):
        return self._current_question

    @current_question.setter
    def current_question(self, question):
        if isinstance(question, Question):
            self._users_answers = dict.fromkeys(self._users_answers, None)
            self._order = []
            self._current_question = question
            random.shuffle(self._shuffled_answers)

    def start_game(self, game):
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
        self.__current_game.save_to_db('games')
        for user in self.loaded_users:
            user.save_to_db('users')

    def consider_question(self):
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
        if isinstance(user, User):
            self._users_answers[user.name] = None
            self._score[user.name] = 0
            self._loaded_users[user.name] = user
        else:
            raise TypeError

    def get_known_questions(self):
        known_questions_codes = set()
        for user in self.loaded_users:
            for question in user.questions:
                known_questions_codes.add(question)
        return list(known_questions_codes)

    def register_answer(self, user_name, choice):
        if self.__current_game:
            try:
                self._users_answers[user_name] = [
                    'A', 'B', 'C', 'D'].index(choice)
            except ValueError:
                print('Invalid answer')
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
        self.current_question = Question.get_unknown_question(
            self.db, self.get_known_questions(), 'questions')

    def propose_game(self):
        proposed_game = Game.load_by_users(
            self.db, [x._id for x in self.loaded_users], 'games')
        return proposed_game or Game(self.db)
