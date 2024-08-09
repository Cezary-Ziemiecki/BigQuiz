import json
import os
from app.quiz.records import User, Game

from flask import Blueprint, Response
from pymongo.mongo_client import MongoClient

from .models import Quiz

blueprint = Blueprint('quiz', __name__)
uri = "mongodb+srv://manager:manager2000@bigquiz.5ex4d.mongodb.net/?retryWrites=true&w=majority&appName=BigQuiz"
myclient = MongoClient(uri)
mydb = myclient["BIGQUIZ"]
quiz = Quiz()


@blueprint.route('/register_user/<user_name>')
def register_user(user_name):
    user = User.load_by_name(mydb, user_name, 'users')
    quiz.register_user(user)
    for x in quiz.loaded_users:
        print(f"{x.name}: {x.questions}")
    return Response(json.dumps(True), mimetype='app/json')


@blueprint.route('/load_game')
def load_game():
    game = Game.load_by_users(
        mydb, [x._id for x in quiz.loaded_users], 'games')
    print(game.questions)
    return Response(json.dumps(True), mimetype='app/json')
