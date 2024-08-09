from quiz.game import Game, User, Question
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
uri = "mongodb+srv://manager:manager2000@bigquiz.5ex4d.mongodb.net/?retryWrites=true&w=majority&appName=BigQuiz"
myclient = MongoClient(uri)
mydb = myclient["BIGQUIZ"]

test = Game.load_by_id(mydb, ObjectId('66b289cf1279597ce6a3c889'))
print(test._id)
print(test.winner)
print(list(test.users))
print(test.questions)

Czarek = User.load_by_id(mydb, ObjectId('66b2880d1279597ce6a3c888'))
print(Czarek._id)
print(list(Czarek.games))
print(Czarek.questions)
Ania = User.load_by_id(mydb, ObjectId('66b4fe33319b66bb55263c4a'))
print(Ania._id)
print(list(Ania.games))
print(Ania.questions)

One = Question.load_by_id(mydb, ObjectId('66b287a21279597ce6a3c887'))

print(One.question)
print(One.correct_answer)
print(One.incorrect_answers)
print(One.question_code)

Two = Question(mydb)
Two.load_new_question()
print(Two.question)
print(Two.correct_answer)
print(Two.incorrect_answers)
print(Two.question_code)
print(Two._id)
Two.save_to_db('questions')
print(Two._id)
