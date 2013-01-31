import argparse
import getpass

from weblab.admin.script import Creation
import sqlalchemy
import traceback

from wlcloud.deploymentsettings import DEFAULT_DEPLOYMENT_SETTINGS, MIN_PORT

def connect(user, passwd):
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    
    engine = sqlalchemy.create_engine(conn_string)
    
    return engine

if __name__ == '__main__':
    #Set arguments
    parser = argparse.ArgumentParser(description="Database creator creates a set of idle databases to be used by the WebLab-Deusto instances.")

    parser.add_argument('-p', '--prefix', metavar="PREFIX",
                        help="database prefix",
                        type=str,
                        required=True)
    
    parser.add_argument('-s', '--start', metavar="START_PORT",
                        help="Start point for databases",
                        type=int,
                        required=False,
                        default=MIN_PORT)
    
    parser.add_argument('-e', '--end', metavar="END_PORT",
                        help="End point for databases",
                        type=int,
                        required=True)

    parser.add_argument('-u', '--db-user', dest='user', metavar="USER",
                        help="Database user",
                        type=str, default=DEFAULT_DEPLOYMENT_SETTINGS[Creation.DB_USER])

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
