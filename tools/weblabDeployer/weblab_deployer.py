from flask import Flask
import settings



app = Flask(__name__)
app.config.from_object(settings)

@app.route('/')
def index():
    raise Exception('Hi I\'m an exception!')
    return 'This is not the funciton that you want'


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
