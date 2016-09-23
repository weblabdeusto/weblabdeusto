import datetime
from flask import render_template, request, url_for, redirect, flash
from flask_wtf import validators
from sqlalchemy.orm import joinedload

from weblab.core.wl import weblab_api
from weblab.core.exc import SessionNotFoundError
from weblab.core.i18n import gettext

from flask_wtf import Form
from wtforms import StringField, validators, PasswordField


class RegistrationForm(Form):
    login = StringField('Login', [
        validators.Length(min=4, max=25),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('verification', message='Passwords must match')
    ])
    full_name = StringField('Full name', [
        validators.DataRequired()
    ])
    verification = PasswordField('Repeat password', [
        validators.DataRequired()
    ])
    email = StringField('Email', [
        validators.Length(min=6, max=35),
        validators.Email(),
        validators.DataRequired()
    ])


@weblab_api.route_webclient("/invitation/", methods=["GET", "POST"])
def invitation_list():
    """
    Shows a list of invitations, but only in DEBUG mode.
    :return:
    """
    # print("DIR: %r" % ((weblab_api.config._values)))

    # TODO: The following doesn't work, so for now, it is commented out.
    # if not weblab_api.app.config.get('DEBUG'):
    #     return "List of invitations is only visible in DEBUG mode"

    # Retrieve the list of invitations.
    from weblab.db.model import DbInvitation
    db_session = weblab_api.db.Session()
    invitations = db_session.query(DbInvitation).options(joinedload('group')).all()
    db_session.close()

    # TODO: Having to close the session and load through joinedload to avoid lazy loading of .group.name is kinda
    # ugly. Check whether that is really necessary.

    return render_template("webclient/invitations_list.html", invitations=invitations)

@weblab_api.route_webclient("/invitation/<id>/register", methods=["GET", "POST"])
def invitation_register(id):

    form = RegistrationForm(request.form)

    db_session = weblab_api.db.Session()

    invitation = weblab_api.db.get_invitation(db_session, id)
    if invitation is None:
        # TODO: Render "invitation does not exist" page.
        return "Invitation does not exist"

    # Save the group_name for later
    group_name = invitation.group.name

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
        return render_template("webclient/registration_form.html", form=form)

    # If this was a POST then we must try to create the user.
    elif request.method == "POST" and form.validate():

        login = form.login.data
        password = form.password.data
        full_name = form.full_name.data
        email = form.email.data

        user = weblab_api.db.get_user(login)
        if user is not None:
            return "User exists already"


        weblab_api.db.create_db_user(login, full_name, email, password, 'student')

        weblab_api.db.accept_invitation(login, invitation.unique_id, group_name, True)

        flash(gettext('Registration done and invitation accepted'))

        return redirect(url_for(".login", _external=True, _scheme=request.scheme))
    else:
        return render_template("webclient/registration_form.html", form=form)



@weblab_api.route_webclient("/invitation/<id>", methods=["GET", "POST"])
def invitation(id):

    db_session = weblab_api.db.Session()

    invitation = weblab_api.db.get_invitation(db_session, id)
    if invitation is None:
        # TODO: Render "invitation does not exist" page.
        return "Invitation does not exist"

    # Get the group name for later.
    group_name = invitation.group.name

    can_accept, why = invitation.can_accept()

    db_session.close()

    if not can_accept:

        if why == "expired":
            error_message =  "Invitation has expired"
            return render_template("webclient/error.html",error_message=error_message)

        elif why == "limit":
            error_message = "Too many people have used this invitation already"
            return render_template("webclient/error.html", error_message=error_message)

        else:
            error_message = "Cannot accept invitation: " + why
            return render_template("webclient/error.html", error_message=error_message)

    login = None
    try:
        weblab_api.api.check_user_session()
        user_session = True
        login = weblab_api.current_user.login
        login_url = None
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

        weblab_api.db.accept_invitation(login, invitation.unique_id, group_name, False)

        flash(gettext('Invitation accepted'))

        return redirect(url_for(".labs"))

@weblab_api.route_webclient("/invitation/<id>/logout", methods=["GET"])
def invitation_logout(id):
    try:
        weblab_api.api.logout()
    except SessionNotFoundError:
        # We weren't logged in but it doesn't matter because we want to logout anyway.
        pass
    return redirect(url_for(".invitation",id=id,_external=True,_scheme=request.scheme))
