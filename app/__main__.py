#!/usr/bin/env python3

from flask import Flask, request, abort
from app_utils import validate_filenames, validate_args, get_contents

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/data', methods=['GET'])
def hand_out_json():
    # validate request args
    if not validate_args(request.args):
        abort(400, "Unexpected parameters passed")

    start = request.args.get("start")
    end = request.args.get("end")

    # validate start and end
    if not validate_filenames(start, end):
        abort(400, "Parameter passed with invalid ISO 8601 format")

    return get_contents(start=start, end=end),\
        {"Content-Type": "application/json"}

if __name__ == "__main__":
    app.run(host='0.0.0.0')