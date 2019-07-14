from flask import Flask, request, make_response, jsonify, render_template
from pymongo import MongoClient
from user import facebookUser
import facebook



app = Flask(__name__, template_folder='templates')
client = MongoClient()

database = client.workouts
exercises = database.exercises

#create a facebookUser Instance
currentUser = facebookUser

#Use the facebook graphAPI to retrieve user info
graph = facebook.GraphAPI(access_token="EAAE8MYlgcvUBAJ979GWMwZBQS4zXBUjQa4H0wT5o0MGE0LHXvviagCXzPzx9ARCnrT5JiDtwSnB6XbHdsDhhYZB3lPwTOY2ZCmhYSWvMmJslnFjuIr3Hu21e5dm3ZBLr2ZC4bTeTEZBUNXfwTK1qYi6vNdZC5MVZA18X9hdY1rdY8QZDZD")


@app.route('/')
def hello_world():
    #return render_template('index.html')
    postRequestData = request.get_json(force=True)

    # Identify the requested action
    action = postRequestData.get('queryResult').get('action')

    # Get user profile info
    userID = postRequestData.get('queryResult').get('outputContexts').get("parameters").get("facebook_sender_id")
    currentUser.setID(userID)
    userName = graph.get_object(id=currentUser.getID(), fields='first_name')
    currentUser.setName(userName)

    if (action == 'input.welcome'):
        res = welcomeMsg(postRequestData)

    return res;

#Identify the action and return the correct data
@app.route('/webhook', methods=['POST'])
def webhook():
    postRequestData = request.get_json(force=True)

    #Identify the requested action
    action = postRequestData.get('queryResult').get('action')

    #Get user profile info
    userID = postRequestData.get('queryResult').get('outputContexts').get("parameters").get("facebook_sender_id")
    currentUser.setID(userID)
    userName = graph.get_object(id=currentUser.getID(), fields='first_name')
    currentUser.setName(userName)

    if (action == 'input.welcome'):
        res = welcomeMsg(postRequestData)

    elif (action == 'get-response'):
        res = test_intent(postRequestData)

    elif (action == 'legs'):
        res = legDay(postRequestData)

    response = make_response(jsonify({'fulfillmentText': res}))

    return response

def welcomeMsg(req):
    response = "Hey " + currentUser.getName() + ", what can I do for you?"
    return response

def test_intent(req):
    legDayLength = exercises.find_one({"Muscle Group" : "Legs"})['Length']
    response = 'This workout is approximately ' + str(legDayLength)
    return response

def legDay(req):
    legs_data = exercises.find_one({"Muscle Group" : "Legs"})
    response = "Here is your custom workout: \n"
    i = 1
    for ex in legs_data['Exercises']:
        response = response + str(i) + '. ' + ex['name'] + "\n"
        i = i + 1

    return response


if __name__ == '__main__':
    app.run()
