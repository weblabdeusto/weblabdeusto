import getpass

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
    accname = raw_input("SQL root account name: ")
    password = getpass.getpass("SQL root account password: ")

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

    print "[1/6] Previous users wcloud and wcloud_creator cleared if present"

    session.execute("CREATE USER 'wcloud_creator'@'localhost' identified by '%s'" % app.config["DB_WCLOUD_CREATOR_PASSWORD"])
    print "[2/6]"

    session.execute("GRANT CREATE ON `wcloud%`.* to 'wcloud_creator'@'localhost'")
    print "[3/6] Database creation privileges granted on wcloud_creator"

    session.execute("GRANT ALL PRIVILEGES ON `wcloud%`.* TO 'wcloud_creator'@'localhost'")
    print "[4/6] Wcloud databases read/write privileges granted on wcloud_creator."

    session.execute("CREATE USER 'wcloud'@'localhost' IDENTIFIED BY '%s'" % app.config["DB_WCLOUD_PASSWORD"])
    print "[5/6] User wcloud created."

    session.execute("GRANT ALL PRIVILEGES ON `wcloud%`.* TO 'wcloud'@'localhost'")
    print "[6/6] Wcloud databases read/write privileges granted on wcloud."

    print "DONE."

    Session.close_all()

main()
