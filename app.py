from flask import Flask, request, make_response, jsonify, render_template
from pymongo import MongoClient
from user import facebookUser
from webCrawler import crawler
import random

# Web crawler api
spider_man = crawler()

#Facebook graph API
import facebook
FACEBOOK_ACCESS_TOKEN = 'EAAE8MYlgcvUBAJ979GWMwZBQS4zXBUjQa4H0wT5o0MGE0LHXvviagCXzPzx9ARCnrT5JiDtwSnB6XbHdsDhhYZB3lPwTOY2ZCmhYSWvMmJslnFjuIr3Hu21e5dm3ZBLr2ZC4bTeTEZBUNXfwTK1qYi6vNdZC5MVZA18X9hdY1rdY8QZDZD'

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
graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)


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

    elif (action == 'chestWorkout'):
        ex = list(spider_man.webSearch('chest'))
        res = "Here is your chest workout:  \n  \n"

        # Select 10 different exercises
        nums = set()
        while len(nums) < 10:
            num = random.randint(0, len(ex))
            if (num < len(ex)):
                nums.add(num)

        x = 1
        for num in nums:
            res = res + str(x) + ". " + ex[num] + "  \n  \n"
            x = x+1

        response = make_response(jsonify({'fulfillmentText': res}))
        return response


    elif (action == 'retrieveVideo'):
        query = postRequestData.get('queryResult').get('parameters').get('exercise')

        res = youtubeSearch(query)

        response = make_response(jsonify(res))

        return response

    elif (action == 'whatIs'):
        query = list(postRequestData.get('queryResult').get('parameters'))[0]
        res = learnMore(query)
        response = make_response(jsonify(res))
        return response

    elif (action == 'legs'):
        res = legDay(postRequestData)

    elif (action == 'whatIsArms'):
        query = postRequestData.get('queryResult').get('parameters').get('arms')
        res = learnMore(query)
        response = make_response(jsonify(res))
        return response

    elif (action == 'whatIsChest'):
        query = postRequestData.get('queryResult').get('parameters').get('chest')
        res = learnMore(query)
        response = make_response(jsonify(res))
        return response

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
    searchTerm = "How to "+query
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

    videoURL = 'https://youtube.com/watch?v='

    searchResult = youtube.search().list(
        q=searchTerm,
        part='snippet',
        maxResults = 50,
        type='video',
        order='relevance',
        videoDuration='short'
    ).execute()

    acceptableChannels = ['UCEtMRF1ywKMc4sf3EXYyDzw', 'UCSpVHeDGr9UbREhRca0qwsA',
                          'UC4ZfcaoM-ZWSsMhWlr8H8Ig', 'UCKf0UqBiCQI4Ol0To9V0pKQ',
                          'UClSBkB4OF9NREOmVq3OlGtg', 'UCwJfDTNqtM5n-dQBfuuHzYw',
                          'UC5_i5V3xXxdqF5VKVmJWVZQ']

    for i in range(50):
        channelid = searchResult.get('items')[i].get('snippet').get('channelId')
        videoID = searchResult.get('items')[i].get('id').get('videoId')
        title = searchResult.get('items')[i].get('snippet').get('title')
        thumbnail = searchResult.get('items')[i].get('snippet').get('thumbnails').get('high').get('url')

        if channelid in acceptableChannels:
            break

    videoURL = videoURL + videoID


    payload = {
        "fulfillmentMessages":[
            {
                "card": {
                    "title": title,
                    "subtitle": "",
                    "imageUri": thumbnail,
                    "buttons": [
                        {
                            "text": "Play",
                            "postback": videoURL
                        }
                    ]
                }
            }
        ]
    }

    return payload

def learnMore(query):
    try:
        results = spider_man.whatIs(query)
        url = results[0]
        photo = results[1]
        video = results[2]
        title = results[3]

        payload = {
            "fulfillmentMessages":[
                {
                    "card": {
                        "title": title,
                        "subtitle": "",
                        "imageUri": photo,
                        "buttons": [
                            {
                                "text": "Watch",
                                "postback": video
                            },
                            {
                                "text": "Learn More",
                                "postback": url
                            }
                        ]
                    }
                }
            ]
        }

    except:
        payload = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "I missed that, say that again?"
                        ]
                    },
                    "lang": "en"
                }
            ]
        }

    return payload





if __name__ == '__main__':
    app.run()
