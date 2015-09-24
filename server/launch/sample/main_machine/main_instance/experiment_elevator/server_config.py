#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

xilinx_board_type = 'FPGA'
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
xilinx_impact_full_path = ["python","../../src/test/unit/weblab/experiment/devices/xilinx_impact/fake_impact.py" ]

xilinx_programmer_type = 'XilinxImpact' # 'JTagBlazer', 'DigilentAdept'
xilinx_device_to_send_commands = 'SerialPort' # 'HttpDevice'

xilinx_serial_port_is_fake = True

xilinx_batch_content_FPGA = """setMode -bs
setCable -port auto
addDevice -position 1 -file $FILE
Program -p 1
exit
"""

digilent_adept_full_path = ["python","../../src/test/unit/weblab/experiment/devices/digilent_adept/fake_digilent_adept.py" ]
digilent_adept_batch_content = """something with the variable $FILE"""

xilinx_http_device_ip_FPGA        = "192.168.50.138"
xilinx_http_device_port_FPGA      = 80
xilinx_http_device_app_FPGA       = ""

xilinx_programmer_time = 60  # seconds

xilinx_synthesizer_time = 120 # This is the time, in seconds, that we estimate it will take to synthesize VHDL. It is only
                              # applied when raw VHDL is sent, rather than an already synthesized BIT file.
                              
xilinx_adaptive_time = True   # When set to true, the fixed times above will be modified dynamically and automatically.

# * As of now this URL will probably be ignored.
fpga_webcam_url          = '''https://www.weblab.deusto.es/webcam/elevator/image.jpg'''

# Path to the UCF, VHD, and project files, which is also the path where the .BIT files will be
# generated.
xilinx_compiling_files_path = "main_machine/main_instance/experiment_elevator/files"

# Path to the Xilinx tools used for compiling (par, xst, etc). This is not required if those
# command line tools are available from the path.
xilinx_compiling_tools_path = ""

# If true, the xilinx experiment will accept VHD files as input, and synthesize them upon request. True by default.
xilinx_vhd_allowed = True

# If true, the xilinx experiment will accept BIT files as input. True by default.
xilinx_bit_allowed = True
