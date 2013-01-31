import traceback
from wlcloud import db

try:
    db.drop_all()
    db.create_all()
except:
    traceback.print_exc()
    print 
    print "Deployment failed. Do you have postgresql installed and the database created?"
    print 
    print "In Ubuntu, for instance, the following steps are required: "
    print
    print "If using MySQL:"
    print 
    print "  $ mysql -uroot -p"
    print "  mysql> CREATE DATABASE wlcloud DEFAULT CHARACTER SET utf8;"
    print "  Query OK, 1 row affected (0.00 sec)"
    print "  mysql> CREATE USER weblab@localhost IDENTIFIED BY 'weblab';"
    print "  ERROR 1396 (HY000): Operation CREATE USER failed for 'weblab'@'localhost'"
    print "  mysql> CREATE USER weblab@localhost IDENTIFIED BY 'weblab';"
    print "  Query OK, 0 rows affected (0.01 sec)"
    print "  mysql> GRANT ALL PRIVILEGES ON wlcloud.* TO weblab@localhost;"
    print "  Query OK, 0 rows affected (0.00 sec)"
    print 
    print "If using PostgreSQL:"
    print 
    print "  $ sudo apt-get install postgresql"
    print "  $ sudo -u postgres psql postgres"
    print "     \password postgres"
    print "  $sudo -u postgres createdb weblab"
    print 

