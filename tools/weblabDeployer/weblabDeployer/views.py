from weblabDeployer import app

@app.route('/')
def index():
    raise Exception('Hi I\'m an exception!')
    return 'This is not the funciton that you want'