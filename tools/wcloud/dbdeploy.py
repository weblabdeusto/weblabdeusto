import sys
import traceback
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import wcloud.config.wcloud_settings as wcloud_settings
import wcloud.config.wcloud_settings_default as wcloud_settings_default

import getpass



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


    # Clean.

    # Check if wcloud_creator exists and delete it if so
    result = session.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'wcloud_creator')")
    if result.first() == (1,):
        session.execute("DROP USER 'wcloud_creator'@'localhost'")

    # Check if wcloud exists and delete it if so
    result = session.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'wcloud')")
    if result.first() == (1,):
        session.execute("DROP USER 'wcloud'@'localhost'")

    print "[1/5] Previous users wcloud and wcloud_creator cleared if present"

    session.execute("CREATE USER 'wcloud_creator'@'localhost' identified by 'password'")
    print "[2/5] User wcloud_creator created."

    session.execute("GRANT CREATE ON `wcloud%`.* to 'wcloud_creator'@'localhost'")
    print "[3/5] Database creation privileges granted on wcloud_creator"

    session.execute("CREATE USER 'wcloud'@'localhost' IDENTIFIED BY 'password'")
    print "[4/5] User wcloud created."

    session.execute("GRANT ALL PRIVILEGES ON `wcloud%`.* TO 'wcloud'@'localhost'")
    print "[5/5] Wcloud databases read/write privileges granted on wcloud."

    print "DONE."

    Session.close_all()

main()


# TO CREATE THE CREATOR MYSQL ACCOUNT:
# CREATE USER wcloud_creator identified by 'password';
# grant create on `wcloud%`.* to 'wcloud_creator'@'localhost';
# create user wcloud identified by 'password';
# grant all privileges on `wcloud%`.* to wcloud;

