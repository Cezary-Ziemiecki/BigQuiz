import json
from app.quiz.records import User, Game, Question
from flask import Blueprint, Response
from pymongo.mongo_client import MongoClient
from .models import Quiz
from functools import partial

blueprint = Blueprint('quiz', __name__)
uri = "mongodb+srv://manager:manager2000@bigquiz.5ex4d.mongodb.net/?retryWrites=true&w=majority&appName=BigQuiz"
myclient = MongoClient(uri)
mydb = myclient["BIGQUIZ"]
quiz = Quiz(mydb)


def print_game_state(func, quiz):
    def inner(*args, **kwargs):
        print(
            f"Before: {quiz.current_question} | {quiz._score} | {quiz._users_answers} | {quiz._order} | {quiz._shuffled_answers}")
        output = func(*args, **kwargs)
        print(
            f"After: {quiz.current_question} | {quiz._score} | {quiz._users_answers} | {quiz._order} | {quiz._shuffled_answers}")
        return output
    inner.__name__ = func.__name__
    return inner


quiz_state = partial(print_game_state, quiz=quiz)


@blueprint.route('/register_user/<user_name>')
@quiz_state
def register_user(user_name):
    user = User.load_by_name(mydb, user_name, 'users')
    quiz.register_user(user)
    return Response(json.dumps(True), mimetype='app/json')


@blueprint.route('/start_game')
@quiz_state
def start_game():
    quiz.start_game(quiz.propose_game())
    return Response(json.dumps(True), mimetype='app/json')


@blueprint.route('/get_question')
@quiz_state
def get_question():
    quiz.load_next_question()
    return Response(json.dumps(True), mimetype='app/json')


@blueprint.route('/put_answer/<user_name>/<choice>')
@quiz_state
def put_answer(user_name, choice):
    success = quiz.register_answer(user_name, choice)
    return Response(json.dumps(success), mimetype='app/json')


@blueprint.route('/send_x/<user_name>')
@quiz_state
def send_x(user_name):
    quiz.start_game(quiz.propose_game())
    return Response(json.dumps(True), mimetype='app/json')
