#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

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

xilinx_batch_content_FPGA = """setMode -bs
setCable -port auto
addDevice -position 1 -file $FILE
Program -p 1
exit
"""

weblab_xilinx_experiment_xilinx_device = 'FPGA'
weblab_xilinx_experiment_port_number   = 1

