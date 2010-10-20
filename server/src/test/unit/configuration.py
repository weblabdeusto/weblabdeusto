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

xilinx_use_jtag_blazer_to_program = False # if not, 'Xilinx'
xilinx_use_http_to_send_commands  = False # if not, 'SerialPort'

# Only when using Xilinx to program the device:

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

# Only when using JTagBlazer to program the device:

xilinx_jtag_blazer_jbmanager_svf2jsvf_full_path = ["python","./test/unit/weblab/experiment/devices/jtag_blazer/fake_jbmanager_svf2jsvf.py" ]
xilinx_jtag_blazer_jbmanager_target_full_path   = ["python","./test/unit/weblab/experiment/devices/jtag_blazer/fake_jbmanager_target.py" ]


# Only when using Serial Port to send commands to the device:

weblab_xilinx_experiment_port_number   = 1
weblab_xilinx_experiment_xilinx_device = 'PLD'

# Only when using HTTP to send commands to the device:

# Must check the really needed commands for FPGA!
xilinx_jtag_blazer_batch_content_FPGA = """setMode -bs
setMode -bs
setMode -bs
setMode -bs
setCable -port svf -file "$SVF_FILE"
addDevice -p 1 -file "$SOURCE_FILE"
Program -p 1 -e -v
exit
"""

xilinx_jtag_blazer_batch_content_PLD = """setMode -bs
setMode -bs
setMode -bs
setMode -bs
setCable -port svf -file "$SVF_FILE"
addDevice -p 1 -file "$SOURCE_FILE"
Program -p 1 -e -v
exit
"""

xilinx_jtag_blazer_device_ip_FPGA = "192.168.50.137"
xilinx_http_device_ip_FPGA        = "192.168.50.138"
xilinx_http_device_port_FPGA      = 80
xilinx_http_device_app_FPGA       = ""

xilinx_jtag_blazer_device_ip_PLD = "192.168.50.139"
xilinx_http_device_ip_PLD        = "192.168.50.140"
xilinx_http_device_port_PLD      = 80
xilinx_http_device_app_PLD       = ""

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



#####################
# VM configuration  #
#####################

vm_url = "rdp://127.0.0.1:8080"
vm_vm_type = "TestVirtualMachine"
vm_user_manager_type = "TestUserManager"
vm_should_store_image = False



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

