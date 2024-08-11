from constants import MONGO_DB_URI, MONGO_DB_NAME
import json
from app.quiz.records import User
from flask import Blueprint, Response
from pymongo.mongo_client import MongoClient
from .models import Quiz
from functools import partial
from app.libs.tools import print_game_state
blueprint = Blueprint('quiz', __name__)

myclient = MongoClient(MONGO_DB_URI)
mydb = myclient[MONGO_DB_NAME]

quiz = Quiz(mydb)


quiz_state = partial(print_game_state, quiz=quiz)


@blueprint.route('/register_user/<user_name>')
@quiz_state
def register_user(user_name):
    """
        Endpoint for register user in the QuizGame
    Parameters
    ----------
    user_name : str
        User name

    Returns
    -------
    Response JSON
        TODO User register success
    """
    user = User.load_by_name(mydb, user_name, 'users')
    quiz.register_user(user)
    return Response(json.dumps(True), mimetype='app/json')


@blueprint.route('/remove_user/<user_name>')
@quiz_state
def remove_user(user_name):
    """
        Endpoint to remove user from the QuizGame
    Parameters
    ----------
    user_name : str
        User name

    Returns
    -------
    Response JSON
        TODO User removing success
    """
    quiz.remove_user(user_name)
    return Response(json.dumps(True), mimetype='app/json')


@blueprint.route('/start_game')
@quiz_state
def start_game():
    """
        Endpoint to start new game depends on loaded users
    Returns
    -------
    Response JSON
        TODO Game starting success
    """
    quiz.start_game(quiz.propose_game())
    return Response(json.dumps(True), mimetype='app/json')


@blueprint.route('/put_answer/<user_name>/<choice>')
@quiz_state
def put_answer(user_name, choice):
    """_summary_

    Parameters
    ----------
    user_name : str
        _description_
    choice : str
        Given answer in 

    Returns
    -------
    Response JSON
        Answer register success

    TODO EXCEPTIONS
    """
    try:
        answer = ['A', 'B', 'C', 'D'].index(choice)
    except ValueError:
        print('Invalid answer')
        success = False
    else:
        success = quiz.register_answer(
            user_name, answer)
    finally:
        return Response(json.dumps(success), mimetype='app/json')


@blueprint.route('/send_x/<user_name>')
@quiz_state
def send_x(user_name):
    """
        Endpoint to run special action send by third party android app
    Parameters
    ----------
    user_name : str
        User name

    Returns
    -------
    _type_
        TODO Game starting success
    """
    quiz.start_game(quiz.propose_game())
    return Response(json.dumps(True), mimetype='app/json')
