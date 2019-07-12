from flask import Flask, request, make_response, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()

database = client.workouts
workouts = database.workouts

@app.route('/')
def hello_world():
    return 'Hello World!'

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
    return "This is a test response"


if __name__ == '__main__':
    app.run()
