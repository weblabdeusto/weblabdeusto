
from flask import render_template, request, url_for, redirect, flash

from weblab.core.wl import weblab_api
from weblab.core.i18n import gettext



@weblab_api.route_webclient("/invitation/<id>", methods=["GET", "POST"])
def invitation(id):

    # If this was a POST then we must try to create the user.
    if request.method == "POST":

        login = request.values.get("login")
        password = request.values.get("password")
        full_name = request.values.get('full_name')
        verification = request.values.get("verification")
        email = request.values.get("email")

        # TODO: Check if username is in use and if password and verification are equal
        print "Username: {}".format(login)
        print "Full name: {}".format(full_name)
        print "Password: {}".format(password)
        print "Verification: {}".format(verification)
        print "email: {}".format(email)


        # Validate: Check that the user does not exist.

        # Validate: Check that the passwords meets minimum (very minimum) criteria.

        # Validate: Check that the passwords are the same.

        # Validate: Check that the e-mail is valid.


        # Create the new user
        weblab_api.db.create_db_user(login, full_name, email, password, 'student')

        flash(gettext('Registration done'))

        print("USER CREATED")

        return redirect(url_for(".invitation", id=id,_external=True, _scheme=request.scheme))

    return render_template("webclient/invitation.html")