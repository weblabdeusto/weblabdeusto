import sys, os
sys.path.append(os.sep.join(("..","src")))

import libraries
import MySQLdb
    
import random
import getpass

CONFIG_FILENAME = "weblab_administrator_credentials.py"

if os.path.exists(CONFIG_FILENAME):
    import weblab_administrator_credentials as wac
else:
    wl_admin_username = "weblab_admin"
    wl_admin_password = "weblab_admin_password_%s" % random.randint(0, 65535)
    
    open(CONFIG_FILENAME, 'w').write(("wl_admin_username = '%s'\n" + \
                                    "wl_admin_password = '%s'\n") %  (wl_admin_username, wl_admin_password) )
    import weblab_administrator_credentials as wac

username = raw_input("MySQL administrator username (default 'root'): ") or "root"
password = getpass.getpass( "MySQL administrator password: " )

sentence1 = "DROP USER '%s'@'localhost'" % wac.wl_admin_username
sentence2 = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s'" % (wac.wl_admin_username, wac.wl_admin_password)
sentence3 = "GRANT SUPER ON *.* TO '%s'@'localhost' IDENTIFIED BY '%s' WITH GRANT OPTION"  % (wac.wl_admin_username, wac.wl_admin_password)
sentence4 = "GRANT INSERT,UPDATE ON mysql.* TO '%s'@'localhost' IDENTIFIED BY '%s'"  % (wac.wl_admin_username, wac.wl_admin_password)
sentence5 = "GRANT ALL PRIVILEGES ON WebLab.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (wac.wl_admin_username, wac.wl_admin_password)
sentence6 = "GRANT ALL PRIVILEGES ON WebLabSessions.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (wac.wl_admin_username, wac.wl_admin_password)
sentence7 = "GRANT ALL PRIVILEGES ON WebLabCoordination.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (wac.wl_admin_username, wac.wl_admin_password)
sentence8 = "GRANT ALL PRIVILEGES ON WebLabTests.* TO '%s'@'localhost' IDENTIFIED BY '%s';"  % (wac.wl_admin_username, wac.wl_admin_password)

for num, sentence in enumerate((sentence1, sentence2, sentence3, sentence4, sentence5, sentence6, sentence7, sentence8)):
	try:
		connection = MySQLdb.connect(user=username, passwd=password)
		cursor = connection.cursor()
		cursor.execute(sentence)
		connection.commit()
		connection.close()
	except: # IF NOT EXISTS
		if num != 0:
			raise

print "Administrator successfully added."

