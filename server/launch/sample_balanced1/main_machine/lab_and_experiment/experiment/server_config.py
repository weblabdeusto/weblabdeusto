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
