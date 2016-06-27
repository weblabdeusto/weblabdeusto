import datetime
from flask import render_template, request, url_for, redirect, flash
from flask.ext.wtf import validators

from weblab.core.wl import weblab_api
from weblab.core.exc import SessionNotFoundError
from weblab.core.i18n import gettext
from weblab.db.model import DbUser


@weblab_api.route_webclient("/invitation/<id>/register", methods=["GET", "POST"])
def invitation_register(id):

    db_session = weblab_api.db.Session()

    invitation = weblab_api.db.get_invitation(db_session, id)
    if invitation is None:
        # TODO: Render "invitation does not exist" page.
        return "Invitation does not exist"

    can_accept, why = invitation.can_accept()

    db_session.close()

    if not can_accept:

        if why == "expired":
            # TODO: Render "invitation has expired" page.
            return "Invitation has expired"

        elif why == "limit":
            # TODO: Render "max_number reached" page.
            return "Too many people have used this invitation already"

    if request.method == "GET":

        # Render the registration form.
        return render_template("webclient/registration_form.html")

    # If this was a POST then we must try to create the user.
    elif request.method == "POST":

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

        session = weblab_api.db.Session()
        user = session.query(DbUser).filter_by(login=login).one_or_none()
        if user is not None:
            return "User exists already"

        # Validate: Check that the passwords meets minimum (very minimum) criteria.

        # Validate: Check that the passwords are the same.

        # Validate: Check that the e-mail is valid.

        weblab_api.db.create_db_user(login, full_name, email, password, 'student')

        weblab_api.db.accept_invitation(login, invitation.unique_id, invitation.group.name, True)

        flash(gettext('Registration done and invitation accepted'))

        return redirect(url_for(".login", _external=True, _scheme=request.scheme))




@weblab_api.route_webclient("/invitation/<id>", methods=["GET", "POST"])
def invitation(id):

    db_session = weblab_api.db.Session()

    invitation = weblab_api.db.get_invitation(db_session, id)
    if invitation is None:
        # TODO: Render "invitation does not exist" page.
        return "Invitation does not exist"

    can_accept, why = invitation.can_accept()

    db_session.close()

    if not can_accept:

        if why == "expired":
            # TODO: Render "invitation has expired" page.
            return "Invitation has expired"

        elif why == "limit":
            # TODO: Render "max_number reached" page.
            return "Too many people have used this invitation already"

        else:
            # TODO: Cannot accept invitation due to unrecognized cause page.
            return "Cannot accept invitation: " + why

    login = None
    try:
        weblab_api.api.check_user_session()
        user_session = True
        login = weblab_api.current_user.login
    except SessionNotFoundError:
        login_url = url_for('.login', next=url_for('.invitation',id=id, _external=True, scheme=request.scheme),
                            _external=True, scheme=request.scheme)
        user_session = False


    if request.method == "GET":

        return render_template("webclient/invitation.html", id=id, user_session=user_session, login_url = login_url)

    elif request.method == "POST":

        # Accept the invitation. This can only be done (from here) if we have a logged-in account to add the group to.
        if login is None:
            # We have no valid session. We redirect back to the invitation screen.
            flash('error', gettext('You are not logged in'))
            return redirect(url_for(".invitation", id=id))

        weblab_api.db.accept_invitation(login, invitation.unique_id, invitation.group.name, False)

        flash(gettext('Invitation accepted'))

        return redirect(url_for(".labs"))
