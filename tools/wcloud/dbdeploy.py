"""
This is the new DB deployment script.
"""

import getpass
from optparse import OptionParser

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import Flask

import wcloud.config.wcloud_settings as wcloud_settings
import wcloud.config.wcloud_settings_default as wcloud_settings_default


app = Flask(__name__)
app.config.from_object(wcloud_settings_default)
app.config.from_object(wcloud_settings)
app.config.from_envvar('WCLOUD_SETTINGS', silent=True)



def connect_to_database(user, passwd):
    """
    Connects to the MySQL database using the specified username and password.
    Assumes the DB is in localhost and listening on port 3306.

    @param user: Username, which will need to be root to create new databases.
    @param passwd: Password for the Username.

    @return: Connection object and the Session() maker.
    """
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    engine = sqlalchemy.create_engine(conn_string)
    connection = engine.connect()
    connection.execute("SELECT 1")

    Session = sessionmaker(bind=connection)

    return connection, Session


def main():

    parser = OptionParser()
    parser.add_option("-u", "--user", dest="user", action="store",
                      help="MySQL root account name", type="string", default=None)
    parser.add_option("-p", "--password",
                      action="store", dest="password",
                      help="MySQL root password", type="string", default=None)

    (options, args) = parser.parse_args()

    if options.user is None:
        accname = raw_input("SQL root account name: ")
    else:
        accname = options.user

    if options.password is None:
        password = getpass.getpass("SQL root account password: ")
    else:
        password = options.password

    engine, Session = connect_to_database(accname, password)
    session = Session()


    # Check if wcloud_creator exists and delete it if so
    result = session.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'wcloud_creator')")
    if result.first() == (1,):
        session.execute("DROP USER 'wcloud_creator'@'localhost'")

    # Check if wcloud exists and delete it if so
    result = session.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'wcloud')")
    if result.first() == (1,):
        session.execute("DROP USER 'wcloud'@'localhost'")

    # Check if wcloud exists and delete it if so
    result = session.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'wcloudtest')")
    if result.first() == (1,):
        session.execute("DROP USER 'wcloudtest'@'localhost'")

    print "[1/8] Previous users wcloud, wcloud_creator and wcloudtest cleared if present"


    session.execute("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET utf8" % app.config["DB_NAME"])
    print "[2/8] Central wcloud database created if it didn't exist."

    session.execute("CREATE USER 'wcloud_creator'@'localhost' identified by '%s'" % app.config["DB_WCLOUD_CREATOR_PASSWORD"])
    print "[3/8] User wcloud_creator created."

    session.execute("GRANT CREATE ON `wcloud%`.* to 'wcloud_creator'@'localhost'")
    print "[4/8] Database creation privileges granted on wcloud_creator"

    session.execute("GRANT ALL PRIVILEGES ON `wcloud%`.* TO 'wcloud_creator'@'localhost'")
    print "[5/8] Wcloud databases read/write privileges granted on wcloud_creator."

    session.execute("CREATE USER 'wcloud'@'localhost' IDENTIFIED BY '%s'" % app.config["DB_WCLOUD_PASSWORD"])
    print "[6/8] User wcloud created."

    session.execute("GRANT ALL PRIVILEGES ON `wcloud%`.* TO 'wcloud'@'localhost'")
    print "[7/8] Wcloud databases read/write privileges granted on wcloud."

    # For now, the testuser has a default password.
    session.execute("CREATE USER 'wcloudtest'@'localhost' IDENTIFIED BY 'password'")
    session.execute("GRANT ALL PRIVILEGES ON `wcloudtest`.* TO 'wcloud'@'localhost'")
    print "[8/8] Wcloudtest user created and granted privileges for wcloudtest DB"

    print "DONE."

    Session.close_all()

main()
