import json
import os
import sys
from app.app import app
import signal
from app.quiz.records import Game, User, Question
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId


# One = Game.load_by_id(mydb, ObjectId('66b289cf1279597ce6a3c889'))
# print(One._id)
# print(One.winner)
# print(list(One.users))
# # print(One.questions)

# One = Game(mydb)
# print(list(One.users))
# One.users.append(2)
# print(list(One.users))
# One.users.append(ObjectId('66b2880d1279597ce6a3c888'))
# print(list(One.users))
# One.users.append(ObjectId('66b4fe33319b66bb55263c4a'))
# print(list(One.users))
# print('AAA')
# print(One.questions)

# Two = Game.load_by_users(mydb, list(One.users), 'games')
# print(Two.questions)
# Two = Game(mydb)
# print(list(Two.users))

# One = User.load_by_name(mydb, 'Cezary', 'users')
# print(list(One.games))
# Two = User.load_by_name(mydb, 'Ania', 'users')
# print(list(Two.games))
# Three = Game.load_by_users(mydb, [One._id, Two._id], 'games')
# print(Three.questions)

# Three = User(mydb)
# Three.name = 'Hero'
# Three._id = ObjectId('66b646dd8d998398c6c0d1ec')
# Three.save_to_db('users')


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=FRONTEND_PORT, debug=False, ssl_context=('cert.pem', 'key.pem'))
    app.run(host="0.0.0.0", port=5500, debug=False)
