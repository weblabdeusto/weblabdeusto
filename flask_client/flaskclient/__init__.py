from flask import render_template, jsonify, Response
from flaskclient.flask_app_builder import build_flask_app
import requests
import re

flask_app = build_flask_app()
flask_app.config.from_pyfile("../config.py")

# Import the different flask_views. This needs to be exactly here because
# otherwise the @flask_app notation wouldn't work.
import view_index
import view_upload


@flask_app.route("/labs.html")
def labs():
    return render_template("labs.html")


@flask_app.route("/lab.html")
def lab():
    return render_template("lab.html")


@flask_app.route("/contact.html")
def contact():
    return render_template("contact.html")

@flask_app.route("/test.html")
def test():
    return render_template("test.html")


@flask_app.route("/configuration")
def configuration():
    """
    Returns the Weblab configuration JSON file. This is mostly for testing. It will eventually
    be removed. It will also filter comments so that the contents can be parsed as valid JSON.
    @return: Configuration file as a JSON response.
    @rtype: Response
    """
    config = requests.get("https://www.weblab.deusto.es/weblab/client/weblabclientlab/configuration.js")
    js = config.content

    def remove_comments(string):
        """
        Removes comments from a string, supports // and /* formats. From Stack Overflow.
        @param str string: Original text.
        @return: Text without comments.
        @rtype: str
        """
        pattern = r"((?<!\\)\".*?(?<!\\)\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
        # first group captures quoted strings (double or single)
        # second group captures comments (//single-line or /* multi-line */)
        regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
        def _replacer(match):
            # if the 2nd group (capturing comments) is not None,
            # it means we have captured a non-quoted (real) comment string.
            if match.group(2) is not None:
                return "" # so we will return empty to remove the comment
            else: # otherwise, we will return the 1st group
                return match.group(1) # captured quoted-string
        return regex.sub(_replacer, string)

    js = remove_comments(js)

    return Response(js, mimetype="application/json")
