from pprint import pprint

from flask import Flask
from flask import Response
from flask import request

from inverted_index import store_object, match, get_all

app = Flask(__name__)

@app.route('/index/', methods=['POST'])
def add():
    if request.method == 'POST':
        data = request.get_json()
        store_object(data)
        return "done"


@app.route('/search/', methods=['GET'])
def search():
    if request.method == 'GET':
        q = request.args['q']
        return Response(match(q), content_type='application/json')

@app.route('/get/', methods=['GET'])
def get():
    if request.method == 'GET':
        return Response(get_all(), content_type='application/json')

if __name__ == '__main__':
    app.run()
