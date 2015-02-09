import os
import argparse
import getpass

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from wcloud import db, app

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
    parser = argparse.ArgumentParser(description='Deploy the database')
    parser.add_argument('-c', '--create-credentials', dest='create_credentials', action='store_true',
                       default=False, help='Create the database users and grant privileges on the tables.')
    args = parser.parse_args()
    if args.create_credentials:
        accname = raw_input("SQL root account name (default: root): ")
        if not accname:
            accname = 'root'
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

        # Check if wcloud exists and delete it if so
        result = session.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'wcloudtest')")
        if result.first() == (1,):
            session.execute("DROP USER 'wcloudtest'@'localhost'")

        print "[1/9] Previous users wcloud, wcloud_creator and wcloudtest cleared if present"


        session.execute("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET utf8" % app.config["DB_NAME"])
        print "[2/9] Central wcloud database created if it didn't exist."

        session.execute("CREATE USER 'wcloud_creator'@'localhost' identified by '%s'" % app.config["DB_WCLOUD_CREATOR_PASSWORD"])
        print "[3/9] User wcloud_creator created."

        session.execute("GRANT CREATE ON `wcloud%`.* to 'wcloud_creator'@'localhost'")
        print "[4/9] Database creation privileges granted on wcloud_creator"

        session.execute("GRANT ALL PRIVILEGES ON `wcloud%`.* TO 'wcloud_creator'@'localhost'")
        print "[5/9] Wcloud databases read/write privileges granted on wcloud_creator."

        session.execute("CREATE USER 'wcloud'@'localhost' IDENTIFIED BY '%s'" % app.config["DB_WCLOUD_PASSWORD"])
        print "[6/9] User wcloud created."

        session.execute("GRANT ALL PRIVILEGES ON `wcloud%`.* TO 'wcloud'@'localhost'")
        print "[7/9] Wcloud databases read/write privileges granted on wcloud."

        # For now, the testuser has a default password.
        session.execute("CREATE USER 'wcloudtest'@'localhost' IDENTIFIED BY 'password'")
        session.execute("GRANT ALL PRIVILEGES ON `wcloudtest`.* TO 'wcloud'@'localhost'")
        print "[8/9] Wcloudtest user created and granted privileges for wcloudtest DB"
    else:
        print "Credentials not added. Use -c to also create the database user"

    db.drop_all()
    db.session.execute("drop table if exists alembic_version")
    os.system("alembic upgrade head")
    print "[9/9] Tables added"

    print "DONE."

main()
