import sys, os
sys.path.append( os.sep.join( ('..', 'src') ) )

import traceback
import getpass
import datetime
import subprocess
import time

import libraries
import MySQLdb
import weblab.database.Model as Model
import weblab.user_processing.coordinator.CoordinatorModel as CoordinatorModel

import voodoo.sessions.DbLockData as DbLockData
import voodoo.sessions.SessionSqlalchemyData as SessionSqlalchemyData

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    import weblab_administrator_credentials as wac
except ImportError:
    print >> sys.stderr, "Error: weblab_administrator_credentials.py not found. Did you execute create_weblab_administrator.py first?" 
    sys.exit(1)

try:
	from configuration import weblab_db_username, weblab_db_password, core_coordinator_db_username , core_coordinator_db_password, weblab_sessions_db_username, weblab_sessions_db_password
except ImportError, e:
	print >> sys.stderr, "Error: configuration.py doesn't exist or doesn't have all the required parameters: %s " % e
	sys.exit(2)


def create_database(admin_username, admin_password, database_name, new_user, new_password, host = "localhost"):
    args = {
            'DATABASE_NAME' : database_name,
            'USER'          : new_user,
            'PASSWORD'      : new_password,
            'HOST'          : host
        }
    sentence1 = "DROP DATABASE IF EXISTS %(DATABASE_NAME)s;" % args
    sentence2 = "CREATE DATABASE %(DATABASE_NAME)s;" % args
    sentence3 = "GRANT ALL ON %(DATABASE_NAME)s.* TO %(USER)s@%(HOST)s IDENTIFIED BY '%(PASSWORD)s';" % args
    
    for sentence in (sentence1, sentence2, sentence3):
        try:
            connection = MySQLdb.connect(user = admin_username, passwd = admin_password)
        except MySQLdb.OperationalError, oe:
            traceback.print_exc()
            print >> sys.stderr, ""
            print >> sys.stderr, "    Tip: did you run create_weblab_administrator.py first?"
            print >> sys.stderr, ""
            sys.exit(-1)
        cursor = connection.cursor()
        cursor.execute(sentence)
        connection.commit()
        connection.close()



create_database(wac.wl_admin_username, wac.wl_admin_password, "WebLab",             weblab_db_username, weblab_db_password)
create_database(wac.wl_admin_username, wac.wl_admin_password, "WebLabTests",        weblab_db_username, weblab_db_password)
create_database(wac.wl_admin_username, wac.wl_admin_password, "WebLabCoordination", core_coordinator_db_username, core_coordinator_db_password)
create_database(wac.wl_admin_username, wac.wl_admin_password, "WebLabSessions",     weblab_sessions_db_username, weblab_sessions_db_password)

print "Databases created."

def _insert_required_initial_data(engine):
    Session = sessionmaker(bind=engine)    
    session = Session()
    
    db = Model.DbAuthType("DB")
    session.add(db)
    ldap = Model.DbAuthType("LDAP")
    session.add(ldap)
    iptrusted = Model.DbAuthType("TRUSTED-IP-ADDRESSES")
    session.add(iptrusted)
    facebook = Model.DbAuthType("FACEBOOK")
    session.add(facebook)
    openid = Model.DbAuthType("OPENID")
    session.add(openid)
    session.commit()

    experiment_allowed = Model.DbPermissionType(
            'experiment_allowed',
            'This type has a parameter which is the permanent ID (not a INT) of an Experiment. Users which have this permission will have access to the experiment defined in this parameter',
            user_applicable = True,
            group_applicable = True,
            ee_applicable = True
    )
    session.add(experiment_allowed)
    experiment_allowed_p1 = Model.DbPermissionTypeParameter(experiment_allowed, 'experiment_permanent_id', 'string', 'the unique name of the experiment')
    session.add(experiment_allowed_p1)
    experiment_allowed_p2 = Model.DbPermissionTypeParameter(experiment_allowed, 'experiment_category_id', 'string', 'the unique name of the category of experiment')
    session.add(experiment_allowed_p2)
    experiment_allowed_p3 = Model.DbPermissionTypeParameter(experiment_allowed, 'time_allowed', 'float', 'Time allowed (in seconds)')
    session.add(experiment_allowed_p3)
    session.commit()    
    
    admin_panel_access = Model.DbPermissionType(
            'admin_panel_access',
            'Users with this permission will be allowed to access the administration panel. The only parameter determines if the user has full_privileges to use the admin panel.',
            user_applicable = True,
            group_applicable = True,
            ee_applicable = True
    )
    session.add(admin_panel_access)
    admin_panel_access_p1 = Model.DbPermissionTypeParameter(admin_panel_access, 'full_privileges', 'bool', 'full privileges (True) or not (False)')
    session.add(admin_panel_access_p1)
    session.commit()

#####################################################################
# 
# Populating main database
# 

print "Populating 'WebLab' database...   \t\t", 

engine = create_engine('mysql://%s:%s@localhost/WebLab' % (weblab_db_username, weblab_db_password), echo = False)
metadata = Model.Base.metadata
metadata.drop_all(engine)
metadata.create_all(engine)

_insert_required_initial_data(engine)

print "[done]"

#####################################################################
# 
# Populating tests database
# 

print "Populating 'WebLabTests' database...   \t\t", 

engine = create_engine('mysql://%s:%s@localhost/WebLabTests' % (weblab_db_username, weblab_db_password), echo = False)
metadata = Model.Base.metadata
metadata.drop_all(engine)
metadata.create_all(engine)   

_insert_required_initial_data(engine)
 
Session = sessionmaker(bind=engine)    
session = Session()

db = session.query(Model.DbAuthType).filter_by(name="DB").one()
ldap = session.query(Model.DbAuthType).filter_by(name="LDAP").one()
iptrusted = session.query(Model.DbAuthType).filter_by(name="TRUSTED-IP-ADDRESSES").one()
facebook = session.query(Model.DbAuthType).filter_by(name="FACEBOOK").one()
openid = session.query(Model.DbAuthType).filter_by(name="OPENID").one()

experiment_allowed = session.query(Model.DbPermissionType).filter_by(name="experiment_allowed").one()
experiment_allowed_p1 = [ p for p in experiment_allowed.parameters if p.name == "experiment_permanent_id" ][0]
experiment_allowed_p2 = [ p for p in experiment_allowed.parameters if p.name == "experiment_category_id" ][0]
experiment_allowed_p3 = [ p for p in experiment_allowed.parameters if p.name == "time_allowed" ][0]

admin_panel_access = session.query(Model.DbPermissionType).filter_by(name="admin_panel_access").one()
admin_panel_access_p1 = [ p for p in admin_panel_access.parameters if p.name == "full_privileges" ][0]

# Auths
weblab_db = Model.DbAuth(db, "WebLab DB", 1)
session.add(weblab_db)

cdk_ldap = Model.DbAuth(ldap, "Configuration of CDK at Deusto", 2, "ldap_uri=ldaps://castor.cdk.deusto.es;domain=cdk.deusto.es;base=dc=cdk,dc=deusto,dc=es")
session.add(cdk_ldap)

deusto_ldap = Model.DbAuth(ldap, "Configuration of DEUSTO at Deusto", 3, "ldap_uri=ldaps://altair.cdk.deusto.es;domain=deusto.es;base=dc=deusto,dc=es")
session.add(deusto_ldap)

localhost_ip = Model.DbAuth(iptrusted, "trusting in localhost", 4, "127.0.0.1")
session.add(localhost_ip)

auth_facebook = Model.DbAuth(facebook, "Facebook", 5)
session.add(auth_facebook)

auth_openid = Model.DbAuth(openid, "OpenID", 6)
session.add(auth_openid)

# Roles
administrator = Model.DbRole("administrator")
session.add(administrator)

professor = Model.DbRole("professor")
session.add(professor)

student = Model.DbRole("student")
session.add(student)

# Users
admin1 = Model.DbUser("admin1", "Name of administrator 1", "weblab@deusto.es", None, administrator)
session.add(admin1)

admin2 = Model.DbUser("admin2", "Name of administrator 2", "weblab@deusto.es", None, administrator)
session.add(admin2)    

admin3 = Model.DbUser("admin3", "Name of administrator 3", "weblab@deusto.es", None, administrator)
session.add(admin3)   

any = Model.DbUser("any", "Name of any", "weblab@deusto.es", None, student)
session.add(any) 

prof1 = Model.DbUser("prof1", "Name of professor 1", "weblab@deusto.es", None, professor)
session.add(prof1)    

prof2 = Model.DbUser("prof2", "Name of professor 2", "weblab@deusto.es", None, professor)
session.add(prof2)    

prof3 = Model.DbUser("prof3", "Name of professor 3", "weblab@deusto.es", None, professor)
session.add(prof3)    

student1 = Model.DbUser("student1", "Name of student 1", "weblab@deusto.es", None, student)
session.add(student1)

student2 = Model.DbUser("student2", "Name of student 2", "weblab@deusto.es", None, student)
session.add(student2)

student3 = Model.DbUser("student3", "Name of student 3", "weblab@deusto.es", None, student)
session.add(student3)

student4 = Model.DbUser("student4", "Name of student 4", "weblab@deusto.es", None, student)
session.add(student4)

student5 = Model.DbUser("student5", "Name of student 5", "weblab@deusto.es", None, student)
session.add(student5)

student6 = Model.DbUser("student6", "Name of student 6", "weblab@deusto.es", None, student)
session.add(student6)

student7 = Model.DbUser("student7", "Name of student 7", "weblab@deusto.es", None, student)
session.add(student7)

student8 = Model.DbUser("student8", "Name of student 8", "weblab@deusto.es", None, student)
session.add(student8)

studentLDAP1 = Model.DbUser("studentLDAP1", "Name of student LDAP1", "weblab@deusto.es", None, student)
session.add(studentLDAP1)

studentLDAP2 = Model.DbUser("studentLDAP2", "Name of student LDAP2", "weblab@deusto.es", None, student)
session.add(studentLDAP2)

studentLDAP3 = Model.DbUser("studentLDAP3", "Name of student LDAP3", "weblab@deusto.es", None, student)
session.add(studentLDAP3)

studentLDAPwithoutUserAuth = Model.DbUser("studentLDAPwithoutUserAuth", "Name of student LDAPwithoutUserAuth", "weblab@deusto.es", None, student)
session.add(studentLDAPwithoutUserAuth)

# External Entities
ee1 = Model.DbExternalEntity("ee1", "Country of ee1", "Description of ee1", "weblab@other.es", "password")
session.add(ee1)

# Authentication
session.add(Model.DbUserAuth(admin1,   weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(admin2,   weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(admin3,   weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(any,      weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(prof1,    weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(prof2,    weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(prof3,    weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student1, weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student2, weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student3, weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student4, weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student5, weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student6, weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student7, weblab_db, "aaaa{thishashdoesnotexist}a776159c8c7ff8b73e43aa54d081979e72511474"))
session.add(Model.DbUserAuth(student8, weblab_db, "this.format.is.not.valid.for.the.password"))
session.add(Model.DbUserAuth(any,      auth_facebook, "1168497114"))
session.add(Model.DbUserAuth(studentLDAP1, cdk_ldap))
session.add(Model.DbUserAuth(studentLDAP2, cdk_ldap))
session.add(Model.DbUserAuth(studentLDAP3, deusto_ldap))

# Groups
groupCourse0809 = Model.DbGroup("Course 2008/09")
groupCourse0809.users.append(student1)
groupCourse0809.users.append(student2)
session.add(groupCourse0809)

groupMechatronics = Model.DbGroup("Mechatronics", groupCourse0809)
groupMechatronics.users.append(student3)
groupMechatronics.users.append(student4)
session.add(groupMechatronics)

groupTelecomunications = Model.DbGroup("Telecomunications", groupCourse0809)
groupTelecomunications.users.append(student5)
groupTelecomunications.users.append(student6)
session.add(groupTelecomunications)

groupCourse0910 = Model.DbGroup("Course 2009/10")
groupCourse0910.users.append(student1)
groupCourse0910.users.append(student2)    
groupCourse0910.users.append(student3)   
groupCourse0910.users.append(student4)   
groupCourse0910.users.append(student5)   
groupCourse0910.users.append(student6)   
session.add(groupCourse0910)

# Experiment Categories
cat_dummy = Model.DbExperimentCategory("Dummy experiments")
session.add(cat_dummy)

cat_pld = Model.DbExperimentCategory("PLD experiments")
session.add(cat_pld)

cat_fpga = Model.DbExperimentCategory("FPGA experiments")
session.add(cat_fpga)

cat_xilinx = Model.DbExperimentCategory("Xilinx experiments")
session.add(cat_pld)

cat_gpib = Model.DbExperimentCategory("GPIB experiments")
session.add(cat_gpib)

cat_pic = Model.DbExperimentCategory("PIC experiments")
session.add(cat_pic)

# Experiments
start_date = datetime.datetime.utcnow()
end_date = start_date.replace(year=start_date.year+10)

dummy = Model.DbExperiment("ud-dummy", cat_dummy, start_date, end_date)
session.add(dummy)

flashdummy = Model.DbExperiment("flashdummy", cat_dummy, start_date, end_date)
session.add(flashdummy)

javadummy = Model.DbExperiment("javadummy", cat_dummy, start_date, end_date)
session.add(javadummy)

logic = Model.DbExperiment("ud-logic", cat_pic, start_date, end_date)
session.add(logic)

pld = Model.DbExperiment("ud-pld", cat_pld, start_date, end_date)
session.add(pld)

demo_pld = Model.DbExperiment("ud-demo-pld", cat_pld, start_date, end_date)
session.add(demo_pld)

pld2 = Model.DbExperiment("ud-pld2", cat_pld, start_date, end_date)
session.add(pld2)

fpga = Model.DbExperiment("ud-fpga", cat_fpga, start_date, end_date)
session.add(fpga)

demo_fpga = Model.DbExperiment("ud-demo-fpga", cat_fpga, start_date, end_date)
session.add(demo_fpga)

demo_xilinx = Model.DbExperiment("ud-demo-xilinx", cat_xilinx, start_date, end_date)
session.add(demo_xilinx)

gpib = Model.DbExperiment("ud-gpib", cat_gpib, start_date, end_date)
session.add(gpib)

pic = Model.DbExperiment("ud-pic", cat_pic, start_date, end_date)
session.add(pic)

pic2 = Model.DbExperiment("ud-pic2", cat_pic, start_date, end_date)
session.add(pic2)

visirtest = Model.DbExperiment("visirtest", cat_dummy, start_date, end_date)
session.add(visirtest)

vm = Model.DbExperiment("vm", cat_dummy, start_date, end_date)
session.add(vm)

vm_win = Model.DbExperiment("vm-win", cat_dummy, start_date, end_date)
session.add(vm_win)

# Permissions
gp_course0809_fpga_allowed = Model.DbGroupPermission(
    groupCourse0809,
    experiment_allowed.group_applicable,
    "Course 2008/09::weblab-fpga",
    datetime.datetime.utcnow(),
    "Permission for group Course 2008/09 to use WebLab-FPGA"
)
session.add(gp_course0809_fpga_allowed)
gp_course0809_fpga_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_fpga_allowed, experiment_allowed_p1, "ud-fpga")
session.add(gp_course0809_fpga_allowed_p1)
gp_course0809_fpga_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_fpga_allowed, experiment_allowed_p2, "FPGA experiments")
session.add(gp_course0809_fpga_allowed_p2)
gp_course0809_fpga_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_fpga_allowed, experiment_allowed_p3, "300")
session.add(gp_course0809_fpga_allowed_p3)

gp_course0809_flashdummy_allowed = Model.DbGroupPermission(
    groupCourse0809,
    experiment_allowed.group_applicable,
    "Course 2008/09::weblab-flashdummy",
    datetime.datetime.utcnow(),
    "Permission for group Course 2008/09 to use WebLab-FlashDummy"
)
session.add(gp_course0809_flashdummy_allowed)
gp_course0809_flashdummy_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_flashdummy_allowed, experiment_allowed_p1, "flashdummy")
session.add(gp_course0809_flashdummy_allowed_p1)
gp_course0809_flashdummy_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_flashdummy_allowed, experiment_allowed_p2, "Dummy experiments")
session.add(gp_course0809_flashdummy_allowed_p2)
gp_course0809_flashdummy_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_flashdummy_allowed, experiment_allowed_p3, "30")
session.add(gp_course0809_flashdummy_allowed_p3)

gp_course0809_javadummy_allowed = Model.DbGroupPermission(
    groupCourse0809,
    experiment_allowed.group_applicable,
    "Course 2008/09::weblab-javadummy",
    datetime.datetime.utcnow(),
    "Permission for group Course 2008/09 to use WebLab-JavaDummy"
)
session.add(gp_course0809_javadummy_allowed)
gp_course0809_javadummy_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_javadummy_allowed, experiment_allowed_p1, "javadummy")
session.add(gp_course0809_javadummy_allowed_p1)
gp_course0809_javadummy_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_javadummy_allowed, experiment_allowed_p2, "Dummy experiments")
session.add(gp_course0809_javadummy_allowed_p2)
gp_course0809_javadummy_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_javadummy_allowed, experiment_allowed_p3, "30")
session.add(gp_course0809_javadummy_allowed_p3)

gp_course0809_logic_allowed = Model.DbGroupPermission(
    groupCourse0809,
    experiment_allowed.group_applicable,
    "Course 2008/09::weblab-logic",
    datetime.datetime.utcnow(),
    "Permission for group Course 2008/09 to use WebLab-Logic"
)
session.add(gp_course0809_logic_allowed)
gp_course0809_logic_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_logic_allowed, experiment_allowed_p1, "ud-logic")
session.add(gp_course0809_logic_allowed_p1)
gp_course0809_logic_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_logic_allowed, experiment_allowed_p2, "Dummy experiments")
session.add(gp_course0809_logic_allowed_p2)
gp_course0809_logic_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_logic_allowed, experiment_allowed_p3, "150")
session.add(gp_course0809_logic_allowed_p3)

gp_course0809_dummy_allowed = Model.DbGroupPermission(
    groupCourse0809,
    experiment_allowed.group_applicable,
    "Course 2008/09::weblab-dummy",
    datetime.datetime.utcnow(),
    "Permission for group Course 2008/09 to use WebLab-Dummy"
)
session.add(gp_course0809_dummy_allowed)
gp_course0809_dummy_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_dummy_allowed, experiment_allowed_p1, "ud-dummy")
session.add(gp_course0809_dummy_allowed_p1)
gp_course0809_dummy_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_dummy_allowed, experiment_allowed_p2, "Dummy experiments")
session.add(gp_course0809_dummy_allowed_p2)
gp_course0809_dummy_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_dummy_allowed, experiment_allowed_p3, "150")
session.add(gp_course0809_dummy_allowed_p3)

gp_course0910_fpga_allowed = Model.DbGroupPermission(
    groupCourse0910,
    experiment_allowed.group_applicable,
    "Course 2009/10::weblab-fpga",
    datetime.datetime.utcnow(),
    "Permission for group Course 2009/10 to use WebLab-FPGA"
)
session.add(gp_course0910_fpga_allowed)
gp_course0910_fpga_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0910_fpga_allowed, experiment_allowed_p1, "ud-fpga")
session.add(gp_course0910_fpga_allowed_p1)
gp_course0910_fpga_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0910_fpga_allowed, experiment_allowed_p2, "FPGA experiments")
session.add(gp_course0910_fpga_allowed_p2)
gp_course0910_fpga_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0910_fpga_allowed, experiment_allowed_p3, "300")
session.add(gp_course0910_fpga_allowed_p3)

up_student2_pld_allowed = Model.DbUserPermission(
    student2,
    experiment_allowed.group_applicable,
    "student2::weblab-pld",
    datetime.datetime.utcnow(),
    "Permission for student2 to use WebLab-PLD"
)
session.add(up_student2_pld_allowed)
up_student2_pld_allowed_p1 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p1, "ud-pld")
session.add(up_student2_pld_allowed_p1)
up_student2_pld_allowed_p2 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p2, "PLD experiments")
session.add(up_student2_pld_allowed_p2)
up_student2_pld_allowed_p3 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p3, "100")
session.add(up_student2_pld_allowed_p3)    

up_student6_pld_allowed = Model.DbUserPermission(
    student6,
    experiment_allowed.group_applicable,
    "student6::weblab-pld",
    datetime.datetime.utcnow(),
    "Permission for student6 to use WebLab-PLD"
)
session.add(up_student6_pld_allowed)
up_student6_pld_allowed_p1 = Model.DbUserPermissionParameter(up_student6_pld_allowed, experiment_allowed_p1, "ud-pld")
session.add(up_student6_pld_allowed_p1)
up_student6_pld_allowed_p2 = Model.DbUserPermissionParameter(up_student6_pld_allowed, experiment_allowed_p2, "PLD experiments")
session.add(up_student6_pld_allowed_p2)
up_student6_pld_allowed_p3 = Model.DbUserPermissionParameter(up_student6_pld_allowed, experiment_allowed_p3, "140")
session.add(up_student6_pld_allowed_p3)    

up_any_visirtest_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-visirtest",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-VisirTest"
)

session.add(up_any_visirtest_allowed)
up_any_visirtest_allowed_p1 = Model.DbUserPermissionParameter(up_any_visirtest_allowed, experiment_allowed_p1, "visirtest")
session.add(up_any_visirtest_allowed_p1)
up_any_visirtest_allowed_p2 = Model.DbUserPermissionParameter(up_any_visirtest_allowed, experiment_allowed_p2, "Dummy experiments")
session.add(up_any_visirtest_allowed_p2)
up_any_visirtest_allowed_p3 = Model.DbUserPermissionParameter(up_any_visirtest_allowed, experiment_allowed_p3, "200")
session.add(up_any_visirtest_allowed_p3)    

up_any_vm_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-vm",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-vm"
)

session.add(up_any_vm_allowed)
up_any_vm_allowed_p1 = Model.DbUserPermissionParameter(up_any_vm_allowed, experiment_allowed_p1, "vm")
session.add(up_any_vm_allowed_p1)
up_any_vm_allowed_p2 = Model.DbUserPermissionParameter(up_any_vm_allowed, experiment_allowed_p2, "Dummy experiments")
session.add(up_any_vm_allowed_p2)
up_any_vm_allowed_p3 = Model.DbUserPermissionParameter(up_any_vm_allowed, experiment_allowed_p3, "200")
session.add(up_any_vm_allowed_p3)    


up_any_vm_win_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-vm-win",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-vm-win"
)


session.add(up_any_vm_win_allowed)
up_any_vm_win_allowed_p1 = Model.DbUserPermissionParameter(up_any_vm_win_allowed, experiment_allowed_p1, "vm-win")
session.add(up_any_vm_win_allowed_p1)
up_any_vm_win_allowed_p2 = Model.DbUserPermissionParameter(up_any_vm_win_allowed, experiment_allowed_p2, "Dummy experiments")
session.add(up_any_vm_win_allowed_p2)
up_any_vm_win_allowed_p3 = Model.DbUserPermissionParameter(up_any_vm_win_allowed, experiment_allowed_p3, "200")

            

up_any_pld_demo_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-pld-demo",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-pld-demo"
)
            
            
session.add(up_any_pld_demo_allowed)
up_any_pld_demo_allowed_p1 = Model.DbUserPermissionParameter(up_any_pld_demo_allowed, experiment_allowed_p1, "ud-demo-pld")
session.add(up_any_pld_demo_allowed_p1)
up_any_pld_demo_allowed_p2 = Model.DbUserPermissionParameter(up_any_pld_demo_allowed, experiment_allowed_p2, "PLD experiments")
session.add(up_any_pld_demo_allowed_p2)
up_any_pld_demo_allowed_p3 = Model.DbUserPermissionParameter(up_any_pld_demo_allowed, experiment_allowed_p3, "200")
session.add(up_any_pld_demo_allowed_p3)    

up_any_fpga_demo_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-fpga-demo",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-fpga-demo"
)

session.add(up_any_fpga_demo_allowed)
up_any_fpga_demo_allowed_p1 = Model.DbUserPermissionParameter(up_any_fpga_demo_allowed, experiment_allowed_p1, "ud-demo-fpga")
session.add(up_any_fpga_demo_allowed_p1)
up_any_fpga_demo_allowed_p2 = Model.DbUserPermissionParameter(up_any_fpga_demo_allowed, experiment_allowed_p2, "FPGA experiments")
session.add(up_any_fpga_demo_allowed_p2)
up_any_fpga_demo_allowed_p3 = Model.DbUserPermissionParameter(up_any_fpga_demo_allowed, experiment_allowed_p3, "200")
session.add(up_any_fpga_demo_allowed_p3)    

up_any_xilinx_demo_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-xilinx-demo",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-xilinx-demo"
)

session.add(up_any_xilinx_demo_allowed)
up_any_xilinx_demo_allowed_p1 = Model.DbUserPermissionParameter(up_any_xilinx_demo_allowed, experiment_allowed_p1, "ud-demo-xilinx")
session.add(up_any_xilinx_demo_allowed_p1)
up_any_xilinx_demo_allowed_p2 = Model.DbUserPermissionParameter(up_any_xilinx_demo_allowed, experiment_allowed_p2, "Xilinx experiments")
session.add(up_any_xilinx_demo_allowed_p2)
up_any_xilinx_demo_allowed_p3 = Model.DbUserPermissionParameter(up_any_xilinx_demo_allowed, experiment_allowed_p3, "200")
session.add(up_any_xilinx_demo_allowed_p3)    

up_student2_gpib_allowed = Model.DbUserPermission(
    student2,
    experiment_allowed.group_applicable,
    "student2::weblab-gpib",
    datetime.datetime.utcnow(),
    "Permission for student2 to use WebLab-GPIB"
)
session.add(up_student2_gpib_allowed)
up_student2_gpib_allowed_p1 = Model.DbUserPermissionParameter(up_student2_gpib_allowed, experiment_allowed_p1, "ud-gpib")
session.add(up_student2_gpib_allowed_p1)
up_student2_gpib_allowed_p2 = Model.DbUserPermissionParameter(up_student2_gpib_allowed, experiment_allowed_p2, "GPIB experiments")
session.add(up_student2_gpib_allowed_p2)
up_student2_gpib_allowed_p3 = Model.DbUserPermissionParameter(up_student2_gpib_allowed, experiment_allowed_p3, "150")
session.add(up_student2_gpib_allowed_p3)             
            
            
up_any_pic_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-pic",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-pic"
)
session.add(up_any_pic_allowed)
up_any_pic_allowed_p1 = Model.DbUserPermissionParameter(up_any_pic_allowed, experiment_allowed_p1, "ud-pic")
session.add(up_any_pic_allowed_p1)
up_any_pic_allowed_p2 = Model.DbUserPermissionParameter(up_any_pic_allowed, experiment_allowed_p2, "pic experiments")
session.add(up_any_pic_allowed_p2)
up_any_pic_allowed_p3 = Model.DbUserPermissionParameter(up_any_pic_allowed, experiment_allowed_p3, "150")
session.add(up_any_pic_allowed_p3)                

up_any_pic2_allowed = Model.DbUserPermission(
    any,
    experiment_allowed.group_applicable,
    "any::weblab-pic2",
    datetime.datetime.utcnow(),
    "Permission for any to use WebLab-pic2"
)
session.add(up_any_pic2_allowed)
up_any_pic2_allowed_p1 = Model.DbUserPermissionParameter(up_any_pic2_allowed, experiment_allowed_p1, "ud-pic2")
session.add(up_any_pic2_allowed_p1)
up_any_pic2_allowed_p2 = Model.DbUserPermissionParameter(up_any_pic2_allowed, experiment_allowed_p2, "PIC experiments")
session.add(up_any_pic2_allowed_p2)
up_any_pic2_allowed_p3 = Model.DbUserPermissionParameter(up_any_pic2_allowed, experiment_allowed_p3, "150")
session.add(up_any_pic2_allowed_p3)
                        
                       
up_student1_admin_panel_access = Model.DbUserPermission(
    student1,
    admin_panel_access.user_applicable,
    "student1::admin_panel_access",
    datetime.datetime.utcnow(),
    "Access to the admin panel for student1 with full_privileges"
)
session.add(up_student1_admin_panel_access)
up_student1_admin_panel_access_p1 = Model.DbUserPermissionParameter(up_student1_admin_panel_access, admin_panel_access_p1, True)
session.add(up_student1_admin_panel_access_p1)

            
session.commit()

print "[done]"

#####################################################################
# 
# Populating Coordination database
# 


print "Populating 'WebLabCoordination' database...\t",

engine = create_engine('mysql://weblab:weblab@localhost/WebLabCoordination', echo = False)

CoordinatorModel.load()

metadata = CoordinatorModel.Base.metadata
metadata.drop_all(engine)
metadata.create_all(engine)    

print "[done]"

#####################################################################
# 
# Populating Sessions database
# 


print "Populating 'WebLabSessions' database...\t",

engine = create_engine('mysql://wl_session_user:wl_session_user_password@localhost/WebLabSessions', echo = False)

metadata = DbLockData.SessionLockBase.metadata
metadata.drop_all(engine)
metadata.create_all(engine)    

metadata = SessionSqlalchemyData.SessionBase.metadata
metadata.drop_all(engine)
metadata.create_all(engine)   

print "[done]"

