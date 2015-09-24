#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
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
from __future__ import print_function, unicode_literals

import os
import sys

try:
    import MySQLdb
    assert MySQLdb is not None # avoid pyflakes warning
except ImportError:
    try:
        import pymysql_sa
        assert pymysql_sa is not None # avoid pyflakes warning
    except ImportError:
        db_engine = 'sqlite'
    else:
        db_engine = 'mysql'
else:
    db_engine = 'mysql'
session_sqlalchemy_engine      = db_engine
session_lock_sqlalchemy_engine = db_engine

core_coordinator_db_engine     = db_engine
#core_coordinator_db_engine     = 'sqlite'
#core_coordinator_db_name = ':memory:'

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
db_echo     = False

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

###################################
# Sessions database configuration #
###################################

session_mysql_host     = 'localhost'
session_mysql_db_name  = 'WebLabSessions'
session_mysql_username = 'weblab'
session_mysql_password = 'weblab'

session_sqlalchemy_host     = 'localhost'
session_sqlalchemy_db_name  = 'WebLabSessions'
session_sqlalchemy_username = 'weblab'
session_sqlalchemy_password = 'weblab'

session_redis_host      = 'localhost'
session_redis_port      = 6379
session_redis_db_index  = 0


##########################################
# Sessions locker database configuration #
##########################################

session_locker_mysql_host     = 'localhost'
session_locker_mysql_db_name  = 'WebLabSessions'
session_locker_mysql_username = 'weblab'
session_locker_mysql_password = 'weblab'

session_lock_sqlalchemy_host     = 'localhost'
session_lock_sqlalchemy_db_name  = 'WebLabSessions'
session_lock_sqlalchemy_username = 'weblab'
session_lock_sqlalchemy_password = 'weblab'


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

core_facade_bind      = ''
core_facade_port        = 18345

core_facade_port = 18346

########################
# Xilinx Configuration #
########################

weblab_xilinx_experiment_xilinx_device = 'PLD'

xilinx_home = "."
xilinx_impact_full_path = [sys.executable,"./test/unit/weblab/experiment/devices/xilinx_impact/fake_impact.py" ]

xilinx_device_to_program = 'XilinxImpact' # 'JTagBlazer', 'DigilentAdept'
xilinx_device_to_send_commands = 'SerialPort' # 'HttpDevice'

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

# Both when using JTagBlazer or Digilent Adept to program the device:

xilinx_source2svf_batch_content_FPGA = """setMode -bs
setMode -bs
setMode -bs
setMode -bs
setCable -port svf -file "$SVF_FILE"
addDevice -p 1 -file "$SOURCE_FILE"
Program -p 1
exit
"""

xilinx_source2svf_batch_content_PLD = """setMode -bs
setMode -bs
setMode -bs
setMode -bs
setCable -port svf -file "$SVF_FILE"
addDevice -p 1 -file "$SOURCE_FILE"
Program -p 1 -e -v
exit
"""

# Only when using JTagBlazer to program the device:

xilinx_jtag_blazer_jbmanager_svf2jsvf_full_path = []
xilinx_jtag_blazer_jbmanager_target_full_path   = []
xilinx_jtag_blazer_device_ip = "192.168.50.137"

# Only when using Digilent Adept to program the device

digilent_adept_full_path = []
digilent_adept_batch_content = """something with the variable $FILE"""

# Only when using Serial Port to send commands to the device:

weblab_xilinx_experiment_port_number = 1

# Only when using HTTP to send commands to the device:

xilinx_http_device_ip   = "192.168.50.138"
xilinx_http_device_port = 80
xilinx_http_device_app  = ""


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

laboratory_assigned_experiments = {
        'exp1:ud-fpga@FPGA experiments':
            {
                 'coord_address': 'experiment1:WL_SERVER1@WL_MACHINE1',
                 'checkers':
                    (
                        ('WebcamIsUpAndRunningHandler', ("https://...",)),
                        ('HostIsUpAndRunningHandler', ("hostname", 80), {}),
                    )
            },
        'exp1:ud-pld@PLD experiments':
            {
                 'coord_address': 'experiment2:WL_SERVER1@WL_MACHINE1',
                 'checkers':
                    (
                        ('WebcamIsUpAndRunningHandler', ("https://...",)),
                        ('HostIsUpAndRunningHandler', ("hostname", 80)),
                    )
            }
    }

########################################
# User Processing Server configuration #
########################################

core_session_type         = 'Memory'

core_coordinator_laboratory_servers   = {
        "laboratory1:WL_SERVER1@WL_MACHINE1" : {
                        "exp1|ud-fpga|FPGA experiments" : "fpga1@fpga boards",
                        "exp1|ud-pld|PLD experiments"   : "pld1@pld boards",
                    }
    }

core_scheduling_systems = {
        "fpga boards"   : ("PRIORITY_QUEUE", {}),
        "pld boards"     : ("PRIORITY_QUEUE", {}),
        "dummy boards"     : ("PRIORITY_QUEUE", {}),
        "res_type"     : ("PRIORITY_QUEUE", {}),
    }

core_server_url = 'http://localhost/weblab/'

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_universal_identifier       = 'da2579d6-e3b2-11e0-a66a-00216a5807c8'
core_universal_identifier_human = 'server X at Sample university'
core_store_students_programs_path = '.'

####################################
# Coordinator Server configuration #
####################################

coordinator_server_session_type = 'Memory'

####################################
# Proxy Server configuration #
####################################

proxy_store_students_programs_path = "./test/unit/weblab/proxy/files_stored".replace('/',os.sep)
