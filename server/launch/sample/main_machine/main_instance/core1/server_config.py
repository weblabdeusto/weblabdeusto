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

core_coordinator_laboratory_servers = [
    "laboratory1:main_instance@main_machine;exp1|ud-fpga|FPGA experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-pld|PLD experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-gpib|GPIB experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-pic|PIC experiments",    
    "laboratory1:main_instance@main_machine;exp1|ud-dummy|Dummy experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-logic|PIC experiments",
    "laboratory1:main_instance@main_machine;exp1|flashdummy|Dummy experiments",
    "laboratory1:main_instance@main_machine;exp1|javadummy|Dummy experiments",
    "laboratory1:main_instance@main_machine;exp1|visirtest|Dummy experiments"
]
