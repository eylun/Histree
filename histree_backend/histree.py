from flask import Flask, render_template, jsonify, request, Response
from json import JSONDecodeError
from histree_query import HistreeQuery

app = Flask(__name__)


@app.route('/')
def greet():
    return render_template('intro.html')


# Pass in a name and return a dictionary of potential matches names to Wiki IDs
@app.route('/find_matches/<name>')
def find_matches(name: str):
    try:
        response = jsonify(
            HistreeQuery.search_matching_names(name))
    except JSONDecodeError:
        response = Response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# Pass in a Wiki ID and return a json of all their relevant data
@app.route('/person_info/<qid>')
def person_info(qid):
    depth_up = request.args.get(
        'depth_up', default=1, type=int)
    depth_down = request.args.get(
        'depth_down', default=1, type=int)
    try:
        response = jsonify(HistreeQuery.get_tree_from_id(
            qid, branch_up_levels=depth_up, branch_down_levels=depth_down))
    except JSONDecodeError:
        response = Response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# Pass in the Wiki IDs of two people and return a json of their relationship
@app.route('/relationship', methods=['GET'])
def relationship_calculator():
    id1 = request.args.get('id1', default="", type=str)
    id2 = request.args.get('id2', default="", type=str)
    result = {"relationship" : "sibling"}

    try:
        response = jsonify(result)
    except JSONDecodeError:
        response = Response()

    response.headers.add("Access-Control-Allow-Origin", "*")
    return response