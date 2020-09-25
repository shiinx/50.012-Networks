from flask import Flask

from flaskr.db import get_db

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def hello():
    db = get_db()
    return {"some_key": "hello"}


@app.route('/bye')
def bye():
    return 'bye'


if __name__ == '__main__':
    app.run()
