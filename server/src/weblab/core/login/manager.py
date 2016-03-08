from __future__ import print_function, unicode_literals
import time
import traceback

import voodoo.log as log

from weblab.core.login.web import EXTERNAL_MANAGERS

from weblab.core.wl import weblab_api
import weblab.core.login.exc as LoginErrors
from weblab.core.exc import DbUserNotFoundError
from weblab.data import ValidDatabaseSessionId

LOGIN_FAILED_DELAY = 2
NOT_LINKABLE_USERS = 'login_not_linkable_users'
DEFAULT_GROUPS     = 'login_default_groups_for_external_users'
CREATING_EXTERNAL_USERS = 'login_creating_external_users'
LINKING_EXTERNAL_USERS  = 'login_linking_external_users'


class LoginManager(object):
    def __init__(self, db, core_server):
        self._db = db
        self._core_server = core_server

    def login(self, username, password):
        """ do_login(username, password) -> SessionId

        raises (
            LoginErrors.UnableToCompleteOperationError,
            LoginErrors.InvalidCredentialsError
        )
        """
        if not password:
            self._process_invalid()
        db_session_id = self._validate_simple_authn(username, password)
        return self._reserve_session(db_session_id)

    def _process_invalid(self):
        # Add a timeout when fails to authenticate in a normal way.
        time.sleep(LOGIN_FAILED_DELAY)
        raise LoginErrors.InvalidCredentialsError( "Invalid username or password!" )


    def _validate_simple_authn(self, username, credentials):
        """
        When the login() method is called, this method is used with the 
        username and credentials (e.g., password, IP address, etc.). This
        method will only check the SimpleAuthn instances.
        """
        try:
            login, role_name, user_auths  = self._db.retrieve_role_and_user_auths(username)
        except DbUserNotFoundError:
            return self._process_invalid()

        # login could be different to username. 
        # For example, in MySQL, where login = 'pablo' is equivalent to where login = 'pablo '
        # For this reason, we don't trust "username", and retrieve login from the database

        errors = False

        for user_auth in user_auths:
            # Take only those auth types that use a simple interface
            if user_auth.is_simple_authn():
                # With each user auth, try to authenticate the user.
                try:
                    authenticated = user_auth.authenticate(login, credentials)
                except:
                    # If there is an error, the user could not be authenticated.
                    log.log( LoginManager, log.level.Warning, "Username: %s with user_auth %s: ERROR" % (login, user_auth) )
                    log.log_exc( LoginManager, log.level.Warning)
                    errors = True
                    traceback.print_exc()
                    continue
                
                if authenticated:
                    # If authenticated, return that it was correctly authenticated.
                    log.log( LoginManager, log.level.Debug, "Username: %s with user_auth %s: SUCCESS" % (login, user_auth) )
                    return ValidDatabaseSessionId( login, role_name )

                else:
                    # If not authenticated, log it and continue with the next user_auth.
                    log.log( LoginManager, log.level.Warning, "Username: %s with user_auth %s: FAIL" % (login, user_auth) )
        
        if errors:
            # Raise error: there was a server problem and this might be the reason for not 
            # authenticating the user. Examples: LDAP server is down, there is an error in the
            # local database or so.
            raise LoginErrors.LoginError( "Error checking credentials. Contact administrators!" )

        return self._process_invalid()

    def _reserve_session(self, db_session_id):
        session_id, server_route = self._core_server._reserve_session(db_session_id)
        if hasattr(session_id, 'id'):
            weblab_api.ctx.session_id = session_id.id
        else:
            weblab_api.ctx.session_id = session_id
        return session_id

    def extensible_login(self, system, credentials):
        """ The extensible login system receives a system (e.g. FACEBOOK, or OPENID), and checks
        that with that system and certain credentials (in a particular format) identifies the user.
        For example, for Facebook, the system will be FACEBOOK and the credentials will be a base64
        string containing the oauth token which WebLab-Deusto will use to contact Facebook and 
        retrieve the user information. In other systems (such as OpenID), it will be used to 
        check in there is an existing session in the session database.

        The important point of this method is that we do not know the login when calling it. In the 
        method "login", the username is provided, the database is accessed to check what authentication
        mechanisms are used. With these mechanisms, the credentials are validated. Here, it is the 
        opposite way: the system provides a set of credentials and some external mechanism will check 
        who is the user, and once validated, it will check in the database who in WebLab-Deusto is that 
        user.
        """
        external_user_id, _ = self._validate_web_protocol_authn(system, credentials)
        # It's a valid external user, book it if there is a user linked
        try:
            db_session_id = self._db.check_external_credentials(external_user_id, system)
        except DbUserNotFoundError:
            raise LoginErrors.InvalidCredentialsError("%s User ID not found: %s" % (system, external_user_id))

        return self._reserve_session(db_session_id)

    def _validate_web_protocol_authn(self, system, credentials):
        system = system.upper()
        if not system in EXTERNAL_MANAGERS:
            raise LoginErrors.LoginError("Invalid system!")

        external_user_id = EXTERNAL_MANAGERS[system].get_user_id(credentials)
        if external_user_id == "":
            raise LoginErrors.InvalidCredentialsError(
                "Invalid username or password!"
            )
        external_user = EXTERNAL_MANAGERS[system].get_user(credentials)
        return external_user_id, external_user


    def grant_external_credentials(self, username, password, system, credentials):
        """ Links an existing user to the new user. """

        if not self._cfg_manager.get_value(LINKING_EXTERNAL_USERS, True):
            raise LoginErrors.LoginError("Linking external users not enabled!")
        not_linkable_users = self._cfg_manager.get_value(NOT_LINKABLE_USERS, [])
        for not_linkable_user in not_linkable_users:
            if username == not_linkable_user:
                raise LoginErrors.LoginError("Username not linkable!")

        local_db_session_id  = self._validate_simple_authn(username, password)
        external_user_id, _  = self._validate_web_protocol_authn(system, credentials)
        # No exception prior to this: the user is the owner of both username and credentials
        self._db.grant_external_credentials(username, external_user_id, system)
        return self._reserve_session(local_db_session_id)

    def create_external_user(self, system, credentials):
        """ Create a new user using an external system. """

        if not self._cfg_manager.get_value(CREATING_EXTERNAL_USERS, True):
            raise LoginErrors.LoginError("Creating external users not enabled!")
        external_user_id, external_user = self._validate_web_protocol_authn(system, credentials)
        if external_user is None:
            raise LoginErrors.LoginError("Creation of external user not supported by delegated login system!")
        group_names = self._cfg_manager.get_value(DEFAULT_GROUPS, [])
        self._db.create_external_user(external_user, external_user_id, system, group_names)
        return self.extensible_login(system, credentials)
