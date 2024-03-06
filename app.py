from flask import Flask, request, abort
from app.app_utils import validate_filenames, validate_args, get_contents

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>"

# The user can provide the argument "start" to get all data
# Or a single timestamp which means data newer than that timestamp
# Or two timestamps which means data in between those dates
# I should put like DONE in a file to prevent this function from reading
# from an unfinished file (writer still active)
# I should also return the actual filename so that the client
# can request newer files based on the returned one, otherwise a problem
# might arise where they think they got all the data newer but there was
# still files being written
# I can make either a timestamp field and return in the JSON response
# or I could've added timestamps to the records in the data, which is not
# the approach I chose to make, so JSON field it is
# Make this paginated?

# make a filename duckdb db with timestamps only, once the client
# requests range of files, i use duckdb to query which files should be opened
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

    return get_contents(start=start, end=end), {"Content-Type": "application/json"}

if __name__ == "__main__":
    app.run(debug=True)