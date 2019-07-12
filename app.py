from flask import Flask, request, make_response, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()

database = client.workouts
excercises = database.excercises

@app.route('/')
def hello_world():
    return "Welcome to Fitness Chatbot"

#Identify the action and return the correct data
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    action = req.get('queryResult').get('action')

    if (action == 'get-response'):
        res = test_intent(req)

    response = make_response(jsonify({'fulfillmentText': res}))

    return response

def test_intent(req):
    legDayLength = excercises.find_one({"Muscle Group" : "Legs"})['Length']
    response = 'This workout is approximately ' + str(legDayLength)
    return response


if __name__ == '__main__':
    app.run()
