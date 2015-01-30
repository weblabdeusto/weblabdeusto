from flask import render_template, request

from weblab.webclient.web.flask_app import flask_app


@flask_app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith("png"):
            file.save("/tmp/saved.png")
    return render_template("upload.html")