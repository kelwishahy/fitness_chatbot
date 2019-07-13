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

    elif (action == 'legs'):
        res = legDay(req)

    response = make_response(jsonify({'fulfillmentText': res}))

    return response

def test_intent(req):
    legDayLength = excercises.find_one({"Muscle Group" : "Legs"})['Length']
    response = 'This workout is approximately ' + str(legDayLength)
    return response

def legDay(req):
    legs_data = excercises.find_one({"Muscle Group" : "Legs"})
    response = "Here is your custom workout: \n"
    i = 1
    for ex in legs_data['Exercises']:
        response = response + str(i) + '. ' + ex['name']
        i = i + 1

    return response



if __name__ == '__main__':
    app.run()
