import sys
import traceback
from wcloud import db

try:
    db.drop_all()
    db.create_all()
except:
    traceback.print_exc()
    print >> sys.stderr, ""
    print >> sys.stderr, "Deployment failed. Do you have postgresql installed and the database created?"
    print >> sys.stderr, ""
    print >> sys.stderr, "In Ubuntu, for instance, the following steps are required: "
    print >> sys.stderr, ""
    print >> sys.stderr, "If using MySQL:"
    print >> sys.stderr, ""
    print >> sys.stderr, "  $ mysql -uroot -p"
    print >> sys.stderr, "  mysql> CREATE DATABASE wcloud DEFAULT CHARACTER SET utf8;"
    print >> sys.stderr, "  Query OK, 1 row affected (0.00 sec)"
    print >> sys.stderr, "  mysql> CREATE USER weblab@localhost IDENTIFIED BY 'weblab';"
    print >> sys.stderr, "  ERROR 1396 (HY000): Operation CREATE USER failed for 'weblab'@'localhost'"
    print >> sys.stderr, "  mysql> CREATE USER weblab@localhost IDENTIFIED BY 'weblab';"
    print >> sys.stderr, "  Query OK, 0 rows affected (0.01 sec)"
    print >> sys.stderr, "  mysql> GRANT ALL PRIVILEGES ON wcloud.* TO weblab@localhost;"
    print >> sys.stderr, "  Query OK, 0 rows affected (0.00 sec)"
    print >> sys.stderr, ""
    print >> sys.stderr, "If using PostgreSQL:"
    print >> sys.stderr, ""
    print >> sys.stderr, "  $ sudo apt-get install postgresql"
    print >> sys.stderr, "  $ sudo -u postgres psql postgres"
    print >> sys.stderr, "     \password postgres"
    print >> sys.stderr, "  $sudo -u postgres createdb weblab"
    print >> sys.stderr, ""
else:
    print "Deployment succeeded."




# TO CREATE THE CREATOR MYSQL ACCOUNT:
# CREATE USER wcloud_creator identified by 'password';
# grant create on `wcloud%`.* to 'wcloud_creator'@'localhost';
#
# create user wcloud identified by 'password';
# grant all privileges on `wcloud%`.* to wcloud;

