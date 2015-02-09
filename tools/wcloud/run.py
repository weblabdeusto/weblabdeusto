from wcloud import app, db

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
