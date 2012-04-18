
from flask import *


import MySQLdb as dbi
import cgi
import time
import calendar

from configuration import _USERNAME, _PASSWORD, DB_NAME, _FILES_PATH

LIMIT   = 150


app = Flask(__name__)
app.debug = True

import libraries


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/yep/<int:n>")
def yep(n):
    return "Hello " + str(n)

if __name__ == "__main__":
    app.run(port=11000)