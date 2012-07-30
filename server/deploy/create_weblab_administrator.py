import sys, os
sys.path.append(os.sep.join(("..","src")))

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

prefixes   = raw_input("Prefixes: (Sampe: 'Deusto,'). If unsure, press enter:").split(',')
username = raw_input("MySQL administrator username (default 'root'): ") or "root"
password = getpass.getpass( "MySQL administrator password: " )

sentence1  = "DROP USER '%s'@'localhost'" % wac.wl_admin_username
sentence2  = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s'" % (wac.wl_admin_username, wac.wl_admin_password)
sentence3  = "GRANT SUPER ON *.* TO '%s'@'localhost' IDENTIFIED BY '%s' WITH GRANT OPTION"  % (wac.wl_admin_username, wac.wl_admin_password)
sentence4  = "GRANT INSERT,UPDATE ON mysql.* TO '%s'@'localhost' IDENTIFIED BY '%s'"  % (wac.wl_admin_username, wac.wl_admin_password)
sentences  = []
for i in range(1,5):
    sentences.append(locals()['sentence%s' % i])

for prefix in prefixes:
    sentence5  = "GRANT ALL PRIVILEGES ON %sWebLab.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    sentence6  = "GRANT ALL PRIVILEGES ON %sWebLabSessions.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    sentence7  = "GRANT ALL PRIVILEGES ON %sWebLabCoordination.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    sentence8  = "GRANT ALL PRIVILEGES ON %sWebLabCoordination2.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    sentence9  = "GRANT ALL PRIVILEGES ON %sWebLabCoordination3.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    sentence10 = "GRANT ALL PRIVILEGES ON %sWebLabTests.* TO '%s'@'localhost' IDENTIFIED BY '%s';"  % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    sentence11 = "GRANT ALL PRIVILEGES ON %sWebLabTests2.* TO '%s'@'localhost' IDENTIFIED BY '%s';"  % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    sentence12 = "GRANT ALL PRIVILEGES ON %sWebLabTests3.* TO '%s'@'localhost' IDENTIFIED BY '%s';"  % (prefix, wac.wl_admin_username, wac.wl_admin_password)
    for i in range(5, 13):
        sentences.append(locals()['sentence%s' % i])

for num, sentence in enumerate(sentences):
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

