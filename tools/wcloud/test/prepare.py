import sqlalchemy
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from wcloud import models



def prepare_test_database(root_username, root_password):
    """
    Prepares the testing database. Will re-create it if needed.
    The testing database name is fixed to 'wcloudtest'.

    @param root_username: Username for the MySQL root.
    @param root_password: Password for the MySQL root.
    """
    engine = connect(root_username, root_password)

    # Destroy the test databse if it exists already, to create it anew.
    engine.execute("DROP DATABASE IF EXISTS wcloudtest")
    engine.execute("CREATE DATABASE wcloudtest DEFAULT CHARACTER SET utf8")
    engine.execute("USE wcloudtest")

    # Create the schema.
    models.db.metadata.create_all(engine)

    # Get the Session maker and bind it to the engine.
    Session = sessionmaker()
    Session.configure(bind=engine)

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

    print("DONE")





def connect(user, passwd):
    """
    Connects to the MySQL database using the specified username and password.
    Assumes the DB is in localhost and listening on port 3306.

    @param user: Username, which will need to be root to create new databases.
    @param passwd: Password for the Username.
    """
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    engine = sqlalchemy.create_engine(conn_string)
    engine.execute("SELECT 1")
    return engine