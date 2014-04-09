import getpass
import optparse
import sys

from weblab.admin.script import Creation
import sqlalchemy
import traceback

from wcloud.default_settings import DB_USERNAME, DB_PASSWORD
from wcloud.deploymentsettings import DEFAULT_DEPLOYMENT_SETTINGS

def connect(user, passwd):
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    
    engine = sqlalchemy.create_engine(conn_string)
    engine.execute("SELECT 1")
    
    return engine

if __name__ == '__main__':
    #Set arguments
    parser = optparse.OptionParser(usage =  "Database creator creates a set of idle databases to be used by the WebLab-Deusto instances."
                                                   "They will be called {PREFIX}{START_POINT} - {PREFIX}{END_POINT}.\n\n"
                                                   "Example:\n\n"
                                                   "   python db_creator.py -p wcloud -e 1000 -u weblab -w\n\n"
                                                   "Will request the database password for user 'weblab' and will create 1000 databases, from"
                                                   "wcloud0000 to wcloud10000")

    parser.add_option('-p', '--prefix', dest='prefix', metavar="PREFIX",
                        help="database prefix",
                        type='str', default="wcloud")
    
    parser.add_option('-s', '--start', dest='start', metavar="START_POINT",
                        help="Start point for databases (defaults to 0)",
                        type='int',
                        default=0)
    
    parser.add_option('-e', '--end', dest = 'end', metavar="END_POINT",
                        help="End point for databases", default=1000,
                        type='int')

    parser.add_option('-u', '--db-user', dest='user', metavar="USER",
                        help="Database user", default="root",
                        type='str')

    parser.add_option('-w', '--prompt-password', dest='prompt_password',
                        help="Request password", action='store_true',
                        default=False)

    parser.add_option('--db-passwd', dest='db_password', metavar="PASSWORD", 
                        help="Database password",
                        type='str', default=DB_PASSWORD)

    parser.add_option('-d', '--delete', dest='delete',
                        help="Delete databases instead of creating them", action='store_true',
                        default=False)

    args, _ = parser.parse_args()
    if args.delete:
        ensure_deletion = raw_input("You've requested to delete the databases. You will lose all the data. Are you sure? Type 'yes' to confirm or 'no' to cancel: ")
        if ensure_deletion != 'yes':
            print >> sys.stderr, "Operation cancelled by user"
            sys.exit(0)

    if args.prompt_password:
        password = getpass.getpass("Password: ")
    else:
        password = args.db_password

    engine = connect(args.user, password)

    
    for n in range(args.start, args.end):
        if args.delete:
            operation = 'deleting'
        else:
            operation = 'creating'

        db_name = '%s%d' % (args.prefix, n)
        try:
            print("%s database '%s'" % (operation.title(), db_name))
            if args.delete:
                engine.execute("DROP DATABASE %s" % db_name)
            else:
                engine.execute("CREATE DATABASE %s DEFAULT CHARACTER SET utf8" % db_name)
                engine.execute("GRANT ALL PRIVILEGES ON %s.* TO %s@localhost" % (db_name, DB_USERNAME))
        except:
            print("Error %s database '%s'" % (operation, db_name))
            traceback.print_exc()





