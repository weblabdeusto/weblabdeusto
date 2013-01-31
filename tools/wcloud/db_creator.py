import argparse
import getpass

from weblab.admin.script import Creation
import sqlalchemy
import traceback

from wcloud.deploymentsettings import DEFAULT_DEPLOYMENT_SETTINGS

def connect(user, passwd):
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    
    engine = sqlalchemy.create_engine(conn_string)
    engine.execute("SELECT 1")
    
    return engine

if __name__ == '__main__':
    #Set arguments
    parser = argparse.ArgumentParser(description=  "Database creator creates a set of idle databases to be used by the WebLab-Deusto instances."
                                                   "They will be called {PREFIX}{START_POINT} - {PREFIX}{END_POINT}.\n\n"
                                                   "Example:\n\n"
                                                   "   python db_creator.py -p wcloud -e 1000 -u weblab -pw\n\n"
                                                   "Will request the database password for user 'weblab' and will create 1000 databases, from"
                                                   "wcloud0000 to wcloud10000")

    parser.add_argument('-p', '--prefix', metavar="PREFIX",
                        help="database prefix",
                        type=str,
                        required=True)
    
    parser.add_argument('-s', '--start', metavar="START_POINT",
                        help="Start point for databases (defaults to 0)",
                        type=int,
                        required=False,
                        default=0)
    
    parser.add_argument('-e', '--end', metavar="END_POINT",
                        help="End point for databases",
                        type=int,
                        required=True)

    parser.add_argument('-u', '--db-user', dest='user', metavar="USER",
                        help="Database user", default="root",
                        type=str)

    parser.add_argument('-pw', '--prompt-password', dest='prompt_password',
                        help="Request password", action='store_true',
                        default=False)

    parser.add_argument('--db-passwd', dest='db_password', metavar="PASSWORD", 
                        help="Database password",
                        type=str, default=DEFAULT_DEPLOYMENT_SETTINGS[Creation.DB_PASSWD])

    args = parser.parse_args()
    if args.prompt_password:
        password = getpass.getpass("Password: ")
    else:
        password = args.db_password

    engine = connect(args.user, password)

    
    for i in range(args.start, args.end):
        try:
            print("Creating database '%s%d'" % (args.prefix, i))
            engine.execute("CREATE DATABASE %s%d" % (args.prefix, i))
        except:
            print("Error creating database '%s%d'" % (args.prefix, i))
            traceback.print_exc()
