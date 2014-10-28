from flask import Flask, request
from flaskclient.babel import Babel


def build_flask_app():
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True
    flask_app.config["SECRET_KEY"] = "SECRET"

    # Initialize internationalization code.
    if Babel is None:
        print "Not using Babel. Everything will be in English"
    else:
        babel = Babel(flask_app)

        supported_languages = ['en']
        supported_languages.extend([translation.language for translation in babel.list_translations()])

        @babel.localeselector
        def get_locale():
            locale = request.args.get('locale', None)
            if locale is None:
                locale = request.accept_languages.best_match(supported_languages)
            if locale is None:
                locale = 'en'
            return locale

    return flask_app