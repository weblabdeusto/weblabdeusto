# This is meant to be the "key" file to hold the "flask_app" object. This file will be imported from all other
# modules which need to access flask_app, so that circular dependencies are avoided.
# The different views which need to make use of the flask_app object NEED to be imported here.
# from webclient.flask_app_builder import build_flask_app
#
#
#
# flask_app = build_flask_app()
# flask_app.config.from_pyfile("../config.py")



# Import the different flask_views. This needs to be exactly here because
# otherwise the @flask_app notation wouldn't work.
# THOSE ARE NOT REALLY UNUSED.
import view_index
#import view_misc
#import view_upload
#import view_labs
#import view_lab


