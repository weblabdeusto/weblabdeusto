#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

weblab_xilinx_experiment_xilinx_device = 'FPGA'
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
xilinx_impact_full_path = ["python","./tests/unit/weblab/experiment/devices/xilinx_impact/fake_impact.py" ]

xilinx_device_to_program = 'XilinxImpact' # 'JTagBlazer', 'DigilentAdept'
xilinx_device_to_send_commands = 'SerialPort' # 'HttpDevice'

digilent_adept_full_path = ["python","./test/unit/weblab/experiment/devices/digilent_adept/fake_digilent_adept.py" ]
digilent_adept_batch_content = """something with the variable $FILE"""

xilinx_http_device_ip_FPGA        = "192.168.50.138"
xilinx_http_device_port_FPGA      = 80
xilinx_http_device_app_FPGA       = ""

xilinx_batch_content_FPGA = """setMode -bs
setCable -port auto
addDevice -position 1 -file $FILE
Program -p 1
exit
"""

# Though it is not really a FPGA, the webcam url var name depends on the device,
# specified above.
fpga_webcam_url = '''https://www.weblab.deusto.es/webcam/fpga0/image.jpg'''
