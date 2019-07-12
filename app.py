from flask import Flask, request, make_response, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

def test_intent():
    req = request.get_json(force=True)
    action = req.get('queryResult').get('action')
    return {'fulfillmentText': 'This is a test response'}

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
   return make_response(jsonify(test_intent()))


if __name__ == '__main__':
    app.run()
