import sqlalchemy
from sqlalchemy.orm import sessionmaker
from wcloud import models



def prepare_test_database(root_username, root_password):
    """
    Prepares the testing database. Will re-create it if needed.
    The testing database name is fixed to 'wcloudtest'.

    @param root_username: Username for the MySQL root.
    @param root_password: Password for the MySQL root.
    """
    connection = connect(root_username, root_password)

    # Destroy the test databse if it exists already, to create it anew.
    connection.execute("DROP DATABASE IF EXISTS wcloudtest")
    connection.execute("CREATE DATABASE wcloudtest DEFAULT CHARACTER SET utf8")

    # Create the test user as well: weblabtest/weblabtest

    try:
        connection.execute("DROP USER weblabtest@localhost")
    except:
        pass

    connection.execute("CREATE USER weblabtest@localhost IDENTIFIED BY 'weblabtest'")
    connection.execute("GRANT ALL PRIVILEGES ON wcloudtest.* TO weblabtest@localhost")
    connection.execute("USE wcloudtest")

    # Create the schema.
    models.db.metadata.create_all(connection)

    # Get the Session maker and bind it to the engine.
    Session = sessionmaker()
    Session.configure(bind=connection)

    db = Session()
    db._model_changes = {}  # In order to bypass a flask-sqlalchemy vs sqlalchemy issue.

    # Add a test entity.
    testentity = models.Entity("Test Entity", "testentity")
    testentity.logo = ""
    testentity.logo_ext = ""
    testentity.link_url = "http://www.testentity.com"
    testentity.start_port_number = 15000
    testentity.end_port_number = 15050

    # Add a test user.
    testuser = models.User("testuser@testuser.com", "password", "Test User")
    testuser.active = True
    testuser.entity = testentity

    db.add(testentity)
    db.add(testuser)
    db.commit()

    db.close()
    connection.close()






def connect(user, passwd):
    """
    Connects to the MySQL database using the specified username and password.
    Assumes the DB is in localhost and listening on port 3306.

    @param user: Username, which will need to be root to create new databases.
    @param passwd: Password for the Username.
    """
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    engine = sqlalchemy.create_engine(conn_string)
    return engine.connect()