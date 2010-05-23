#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
# 
# This is a configuration sample
# This module will be loaded and reloaded by the ConfigurationManager

import os

#########################
# General configuration #
#########################

debug_mode                = True
server_hostaddress        = 'weblab.deusto.es'
server_admin              = 'weblab@deusto.es'

###############################
# Mail Notifier configuration #
###############################

mail_notification_enabled = False
mail_server_host          = 'rigel.deusto.es'
mail_server_use_tls       = 'yes'
mail_server_helo          = server_hostaddress
mail_notification_sender  = 'weblab@deusto.es'
mail_notification_subject = '[WebLab] CRITICAL ERROR!'

##########################
# Database configuration #
##########################

db_driver   = "MySQLdb"
db_host     = "localhost"
db_database = "WebLabTests"
db_prefix   = "wl_"

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

###################################
# Sessions database configuration #
###################################

session_mysql_host     = 'localhost'
session_mysql_db_name  = 'WebLabSessions'
session_mysql_username = 'wl_session_user'
session_mysql_password = 'wl_session_user_password'

session_sqlalchemy_host     = 'localhost'
session_sqlalchemy_db_name  = 'WebLabSessions'
session_sqlalchemy_username = 'wl_session_user'
session_sqlalchemy_password = 'wl_session_user_password'


##########################################
# Sessions locker database configuration #
##########################################

session_locker_mysql_host     = 'localhost'
session_locker_mysql_db_name  = 'WebLabSessions'
session_locker_mysql_username = 'wl_session_user'
session_locker_mysql_password = 'wl_session_user_password'

session_lock_sqlalchemy_host     = 'localhost'
session_lock_sqlalchemy_db_name  = 'WebLabSessions'
session_lock_sqlalchemy_username = 'wl_session_user'
session_lock_sqlalchemy_password = 'wl_session_user_password'


########################
# Loader configuration #
########################

loader_check_configuration_syntax = True
loader_xsd_path                   = "test/deployments/WebLabSkel/lib/schemas/"

#############################
# Experiments configuration #
#############################

core_experiment_poll_time = 15 # seconds

##############################
# RemoteFacade configuration #
##############################

core_facade_soap_bind       = ''
core_facade_soap_port         = 10123
core_facade_soap_service_name = '/weblab/soap/'

core_facade_json_bind      = ''
core_facade_json_port        = 18345

core_facade_xmlrpc_bind    = ''
core_facade_xmlrpc_port      = 19345

login_facade_soap_bind       = ''
login_facade_soap_port         = 10223
login_facade_soap_service_name = '/weblab/login/soap/'

login_facade_json_bind      = ''
login_facade_json_port        = 18445

login_facade_xmlrpc_bind    = ''
login_facade_xmlrpc_port      = 19445

########################
# Xilinx configuration #
########################

# This should be something like this:
# import os as _os
# xilinx_home = _os.getenv('XILINX_HOME')
# if xilinx_home == None:
#   if _os.name == 'nt':
#       xilinx_home = r'C:\Program Files\Xilinx'
#   elif _os.name == 'posix':
#       xilinx_home = r"/home/nctrun/Xilinx"
# 
# if _os.name == 'nt':
#   xilinx_impact_full_path = [xilinx_home + r'\bin\nt\impact']
# elif _os.name == 'posix':
#   xilinx_impact_full_path = [xilinx_home + r'/bin/lin/impact']

# But for testing we are going to fake it:

xilinx_home = "."
xilinx_impact_full_path = ["python","./test/unit/weblab/experiment/devices/xilinx_impact/fake_impact.py" ]

xilinx_batch_content_FPGA = """setMode -bs
setCable -port auto
addDevice -position 1 -file $FILE
Program -p 1
exit
"""

xilinx_batch_content_PLD  = """setMode -bs
setMode -bs
setCable -port auto
Identify
identifyMPM
assignFile -p 1 -file $FILE
Program -p 1 -e -defaultVersion 0
quit
"""

weblab_xilinx_experiment_xilinx_device = 'PLD'
weblab_xilinx_experiment_port_number   = 1

######################
# GPIB configuration #
######################

fake_compiler_path    = "./test/unit/weblab/experiment/devices/gpib/fake_compiler.py".replace('/',os.sep)
fake_linker_path    = "./test/unit/weblab/experiment/devices/gpib/fake_linker.py".replace('/',os.sep)

# Real ones
#gpib_compiler_command = ['bcc32','-c','$CPP_FILE']
#gpib_linker_command   = ["ilink32","-Tpe","-c","$OBJ_FILE","c0x32,", "$EXE_FILE,",",","visa32","import32","cw32","bidsf"]

gpib_compiler_command = [ 'python', fake_compiler_path, '$CPP_FILE']

gpib_linker_command   = [ 
        'python',
        fake_linker_path, 
        #"ilink32", # ilink32 is the compiler itself
        "-Tpe", 
        "-c", 
        "$OBJ_FILE", 
        "c0x32,", 
        "$EXE_FILE,",
        ",", 
        "visa32", 
        "import32", 
        "cw32", 
        "bidsf"
    ]

gpib_public_output_filename      = 'gpib_gpib.txt'
gpib_public_output_file_filename = 'gpib_salida.txt'

#####################
# PIC configuration #
#####################

pic_tftp_server_hostname = 'localhost'
pic_tftp_server_port     = 69
pic_tftp_server_filename = 'sample_filename'
pic_http_server_hostname = 'localhost'
pic_http_server_port     = 80
pic_http_server_app      = 'pic.cgi'

#########################
# NETWORK configuration #
#########################

network_tftp_server_hostname = 'localhost'
network_tftp_server_port     = 5000
network_tftp_server_filename = 'sample_filename'

###################################
# Laboratory Server configuration #
###################################

laboratory_session_type = 'Memory'

laboratory_assigned_experiments = [
        'exp1|ud-fpga|FPGA experiments;experiment1:WL_SERVER1@WL_MACHINE1',
        'exp1|ud-pld|PLD experiments;experiment2:WL_SERVER1@WL_MACHINE1'
    ]

########################################
# User Processing Server configuration #
########################################

core_session_type         = 'Memory'

core_coordinator_laboratory_servers   = [
        "laboratory1:WL_SERVER1@WL_MACHINE1;exp1|ud-fpga|FPGA experiments",
        "laboratory1:WL_SERVER1@WL_MACHINE1;exp1|ud-pld|PLD experiments",
    ]

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

####################################
# Coordinator Server configuration #
####################################

coordinator_server_session_type = 'Memory'

