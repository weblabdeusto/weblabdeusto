import argparse

from weblab.admin.script import Creation
import sqlalchemy
import traceback

from weblabDeployer.deploymentsettings import DEFAULT_DEPLOYMENT_SETTINGS

def connect():
    conn_string = 'mysql://%s:%s@%s:%d' %\
                (DEFAULT_DEPLOYMENT_SETTINGS[Creation.DB_USER],
                 DEFAULT_DEPLOYMENT_SETTINGS[Creation.DB_PASSWD],
                 '127.0.0.1',
                 3306,)
    
    engine = sqlalchemy.create_engine(conn_string)
    
    return engine

if __name__ == '__main__':
    #Set arguments
    parser = argparse.ArgumentParser(description="Database creator")

    parser.add_argument('-p', '--prefix',
                        help="database prefix",
                        type=str,
                        required=True)
    
    parser.add_argument('-s', '--start',
                        help="Start point for databases",
                        type=int,
                        required=False,
                        default=0)
    
    parser.add_argument('-e', '--end',
                        help="End point for databases",
                        type=int,
                        required=True)
    
    engine = connect()
    args = parser.parse_args()
    
    for i in range(args.start, args.end):
        try:
            print("Creating database '%s%d'" % (args.prefix, i))
            engine.execute("CREATE DATABASE %s%d" % (args.prefix, i))
        except:
            print("Error creating database '%s%d'" % (args.prefix, i))
            traceback.print_exc()
