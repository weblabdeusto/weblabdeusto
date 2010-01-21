import ldap, sys

from users import User
from DbManager import DbManager
from configuration import LDAP_URI, LDAP_AUTH_DOMAIN, LDAP_BASE, LDAP_QUERY, AUTH_INSTANCE_ID

def _parse_result_set(result_set, username):
    user_map = result_set[0][1]
    print "%s %s" % (user_map['givenName'][0], user_map['sn'][0]) #result_set
    givenName = user_map['givenName'][0]
    surname = user_map['sn'][0]
    mail = user_map['mail'][0]
    
    db = DbManager()
    exists = db.user_exists(username)
    has_auth = db.has_auth(username, AUTH_INSTANCE_ID)

    return User(username, givenName, surname, mail, exists, has_auth)


def gather_information(auth_user, auth_pass, usernames):
    con = ldap.initialize(LDAP_URI)
    con.simple_bind_s('%(username)s@%(domain)s' % {
            'username' : auth_user,
            'domain'   : LDAP_AUTH_DOMAIN
        }, auth_pass)

    for username in usernames:
        result_set = con.search_s(
            LDAP_BASE, # base
            ldap.SCOPE_SUBTREE, #scope :-S
            LDAP_QUERY % username, #filter
            ["givenName","sn","mail"] #retrieved attributes (is this ok?)
        )

        if len(result_set) < 1:
            print >>sys.stderr,"User <%s> not found" % username
        elif len(result_set) > 1:
            print >>sys.stderr,"Invalid state: too many users found for username %s" % username
            yield _parse_result_set(result_set, username)
        else:
            yield _parse_result_set(result_set, username)
    con.unbind()