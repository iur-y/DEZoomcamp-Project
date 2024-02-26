from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/data', methods=['GET'])
def hand_out_json():
    second = request.args.get("second")
    minute = request.args.get("minute")
    hour = request.args.get("hour")
    d = {"hour": hour,
         "minute": minute,
         "second": second}
    return d