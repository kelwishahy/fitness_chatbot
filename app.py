from flask import Flask, request, make_response, jsonify, render_template
from pymongo import MongoClient
from user import facebookUser
import facebook

#Youtube Data API V3
from googleapiclient.discovery import build
YOUTUBE_API_KEY = 'AIzaSyAs-iOyMzSgDwIKOTTQ_EgTgkGIeAP3VIE'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'



app = Flask(__name__, template_folder='templates')
client = MongoClient()

database = client.workouts
exercises = database.exercises

#create a facebookUser Instance
currentUser = facebookUser()

#Use the facebook graphAPI to retrieve user info
graph = facebook.GraphAPI(access_token="EAAE8MYlgcvUBAJ979GWMwZBQS4zXBUjQa4H0wT5o0MGE0LHXvviagCXzPzx9ARCnrT5JiDtwSnB6XbHdsDhhYZB3lPwTOY2ZCmhYSWvMmJslnFjuIr3Hu21e5dm3ZBLr2ZC4bTeTEZBUNXfwTK1qYi6vNdZC5MVZA18X9hdY1rdY8QZDZD")


@app.route('/')
def hello_world():
    return render_template('index.html')

#Identify the action and return the correct data
@app.route('/webhook', methods=['POST'])
def webhook():
    postRequestData = request.get_json(force=True)

    #Identify the requested action
    action = postRequestData.get('queryResult').get('action')

    #Get user profile info
    userID = postRequestData.get('queryResult').get('outputContexts')[0].get('parameters').get('facebook_sender_id')
    currentUser.setID(userID)
    userName = str(graph.get_object(id=currentUser.getID(), fields='first_name')['first_name'])
    currentUser.setName(userName)

    if (action == 'input.welcome'):
        res = welcomeMsg(postRequestData)

    elif (action == 'get-response'):
        res = test_intent(postRequestData)

    elif (action == 'retrieveVideo'):
        query = postRequestData.get('queryResult').get('parameters').get('exercise')

        res = youtubeSearch(query)

        res = jsonify(res)

        return make_response(res)

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

def youtubeSearch(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

    videoURL = 'https://youtube.com/w?v='

    searchResult = youtube.search().list(
        q=query,
        part='snippet',
        maxResults = 1,
        type='video',
        order='viewCount'
    ).execute()

    videoID = searchResult.get('items')[0].get('id').get('videoId')

    videoURL = videoURL + videoID

    customPayload = {
        'payload':{
            'facebook':{
                'recipient':{
                    'id':currentUser.getID()
                },
                'message':{
                    "attachment": {
                        "type": "video",
                        "payload": {
                            "url": videoURL,
                            "is_reusable":True
                        }
                    }
                }
            }
        }
    }

    return customPayload

if __name__ == '__main__':
    app.run()
