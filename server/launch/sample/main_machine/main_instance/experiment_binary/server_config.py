#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

xilinx_board_type = 'PLD'
weblab_xilinx_experiment_port_number   = 1

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

xilinx_programmer_type = 'XilinxImpact' # 'DigilentAdept', 'JTagBlazer'
xilinx_device_to_send_commands = 'SerialPort' # 'HttpDevice'

xilinx_jtag_blazer_jbmanager_svf2jsvf_full_path = ["python","./test/unit/weblab/experiment/devices/jtag_blazer/fake_jbmanager_svf2jsvf.py" ]
xilinx_jtag_blazer_jbmanager_target_full_path   = ["python","./test/unit/weblab/experiment/devices/jtag_blazer/fake_jbmanager_target.py" ]

xilinx_jtag_blazer_device_ip_PLD = "192.168.50.137"

xilinx_http_device_ip_PLD        = "192.168.50.138"
xilinx_http_device_port_PLD      = 80
xilinx_http_device_app_PLD       = ""

xilinx_batch_content_PLD  = """setMode -bs
setMode -bs
setCable -port auto
Identify
identifyMPM
assignFile -p 1 -file $FILE
Program -p 1 -e -defaultVersion 0
quit
"""

pld_webcam_url          = '''https://www.weblab.deusto.es/webcam/pld0/image.jpg'''
