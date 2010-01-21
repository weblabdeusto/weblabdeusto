import information_retriever
import generator
import getpass
import pickle

from configuration import LDAP_AUTH_DOMAIN, INPUT_FILE, OUTPUT_FILE, USERS_FILE

class Parser(object):
    
    def __init__(self):
        super(Parser, self).__init__()
        self.authenticate()
        self.read_logins()
        self.get_users_from_ldap()
        self.write_dump()
        self.write_sql()

    def authenticate(self):
        self.username = raw_input("Username (for domain %s): " % LDAP_AUTH_DOMAIN)
        self.password = getpass.getpass("Password: ")

    def read_logins(self):
        # Parse file, one user per line, without a # before the username, space does not support spaces
        self.logins = [ 
                login 
                for login in ( 
                    ''.join(char for char in line if not char.isspace()) 
                    for line in open(INPUT_FILE).readlines()  
                ) 
                if not login.startswith('#')
            ]

    def get_users_from_ldap(self):
        users_information = information_retriever.gather_information(self.username, self.password, self.logins)
        self.users = [ i for i in users_information ]

    def write_dump(self):
        pickle.dump(self.users, open(USERS_FILE, 'w'))

    def write_sql(self):
        sql_code = generator.generate_sql_code(self.users)
        open(OUTPUT_FILE,'w').write(sql_code)
        print "SQL code generated and saved in %s, proceed to enter the information in the database and run launch_mail_them_all.py" % OUTPUT_FILE

if __name__ == "__main__":
    p = Parser()