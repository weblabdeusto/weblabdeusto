#####################################
# Core Server General configuration #
#####################################

core_store_students_programs      = True
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

####################################
# Core Server Facade configuration #
####################################

core_facade_soap_port   = 10123
core_facade_xmlrpc_port = 19345
core_facade_json_port   = 18345

admin_facade_json_port   = 18545

core_web_facade_port   = 19745

######################################
# Core Server Database configuration #
######################################

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

#########################################
# Core Server Coordinator configuration #
#########################################

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_coordinator_laboratory_servers = {
    "laboratory1:main_instance@main_machine" : {
            "exp1|ud-fpga|FPGA experiments"          : "fpga@fpga",
            "exp1|ud-pld|PLD experiments"            : "pld@pld",
            "exp1|ud-demo-pld|PLD experiments"       : "pld@pld",
            "exp1|ud-demo-fpga|FPGA experiments"     : "fpga@fpga",
            "exp1|ud-demo-xilinx|Xilinx experiments" : "pld@pld",
            "exp2|ud-demo-xilinx|Xilinx experiments" : "fpga@fpga",
            "exp1|ud-gpib|GPIB experiments"          : "gpib@gpib",
            "exp1|ud-pic|PIC experiments"            : "pic@pic",
            "exp1|ud-dummy|Dummy experiments"        : "dummy@dummy",
            "exp1|ud-logic|PIC experiments"          : "logic@logic",
            "exp1|flashdummy|Dummy experiments"      : "flashdummy@flashdummy",
            "exp1|javadummy|Dummy experiments"       : "javadummy@javadummy",
            "exp1|visirtest|Dummy experiments"       : "visirtest@visirtest",
            "exp1|vm|Dummy experiments"              : "vm@vm",
            "exp1|vm-win|Dummy experiments"          : "vm-win@vm-win",
        }
}

core_scheduling_systems = {
        "fpga"       : ("PRIORITY_QUEUE", {}),
        "pld"        : ("PRIORITY_QUEUE", {}),
        "gpib"       : ("PRIORITY_QUEUE", {}),
        "pic"        : ("PRIORITY_QUEUE", {}),
        "dummy"      : ("PRIORITY_QUEUE", {}),
        "logic"      : ("PRIORITY_QUEUE", {}),
        "flashdummy" : ("PRIORITY_QUEUE", {}),
        "javadummy"  : ("PRIORITY_QUEUE", {}),
        "visirtest"  : ("PRIORITY_QUEUE", {}),
        "vm"         :("PRIORITY_QUEUE", {}),
        "vm-win"     : ("PRIORITY_QUEUE", {}),
    }
