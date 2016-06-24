
from flask import render_template, request, url_for, redirect, flash
from flask.ext.wtf import validators

from weblab.core.wl import weblab_api
from weblab.core.i18n import gettext

@weblab_api.route_webclient("/invitation/<id>/register", methods=["GET", "POST"])
def invitation_register(id):

    if request.method == "POST":
        # If this is a POST it is a login request.
        #
        username = request.values.get("login")
        password = request.values.get("password")
        full_name = request.values.get('full_name')
        verification = request.values.get("verification")
        email = request.values.get("email")

        #TODO: Check if username is in use and if password and verification are equal
        print "Username: {}".format(username)
        print "Full name: {}".format(verification)
        print "Password: {}".format(password)
        print "Verification: {}".format(verification)
        print "email: {}".format(email)
        return redirect(url_for(".invitation_register", id=id,_external=True, _scheme=request.scheme))

    return render_template("webclient/registration_form.html")

@weblab_api.route_webclient("/invitation/<id>", methods=["GET", "POST"])
def invitation(id):
    if request.method == "POST":
        #Add user to the group here
        return redirect(url_for(".login"))
    return render_template("webclient/invitation.html", id=id)

