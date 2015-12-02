#####################################
# Core Server General configuration #
#####################################
import os
core_store_students_programs      = True
core_store_students_programs_path = os.path.abspath('files_stored')
core_experiment_poll_time         = 30 # seconds

####################################
# Core Server Facade configuration #
####################################

core_facade_port   = 18345




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
    "laboratory:main_instance@main_machine" : {
            "exp1|ud-fpga|FPGA experiments"          : "fpga@fpga",
            "exp1|ud-pld|PLD experiments"            : "pld@pld",
            "exp1|ud-demo-pld|PLD experiments"       : "pld@pld",
            "exp1|ud-demo-fpga|FPGA experiments"     : "fpga@fpga",
            "exp1|ud-demo-xilinx|Xilinx experiments" : "pld@pld",
            "exp2|ud-demo-xilinx|Xilinx experiments" : "fpga@fpga",
            "exp1|ud-gpib|GPIB experiments"          : "gpib@gpib",
            "exp1|ud-dummy|Dummy experiments"        : "dummy@dummy",
            "exp1|ud-dummy-batch|Dummy experiments"  : "dummy-batch@dummy-batch",
            "exp1|ud-logic|PIC experiments"          : "logic@logic",
            "exp1|flashdummy|Dummy experiments"      : "flashdummy@flashdummy",
            "exp1|javadummy|Dummy experiments"       : "javadummy@javadummy",
            "exp1|jsdummy|Dummy experiments"         : "jsdummy@jsdummy",
            "exp1|jsfpga|FPGA experiments"           : "jsfpga@jsfpga",
            "exp1|hwboard-fpga|FPGA experiments"     : "fpga@fpga",
            "exp1|hwboard-fpga-watertank|FPGA experiments" : "fpga@fpga",
            "exp1|visirtest|Dummy experiments"       : "visir1@visir",
            "exp2|visirtest|Dummy experiments"       : "visir2@visir",
            "exp3|visirtest|Dummy experiments"       : "visir3@visir",
            "exp4|visirtest|Dummy experiments"       : "visir4@visir",
            "exp5|visirtest|Dummy experiments"       : "visir5@visir",
            "exp1|visir|Visir experiments"           : "visir1@visir",
            "exp2|visir|Visir experiments"           : "visir2@visir",
            "exp3|visir|Visir experiments"           : "visir3@visir",
            "exp4|visir|Visir experiments"           : "visir4@visir",
            "exp5|visir|Visir experiments"           : "visir5@visir",
            "exp6|visir-html5|Visir experiments"     : "visir6@visir",
            "exp1|vm|Dummy experiments"              : "vm@vm",
            "exp1|vm-win|Dummy experiments"          : "vm-win@vm-win",
            "exp1|robot-standard|Robot experiments"  : "robot@robot",
            "exp1|robot-movement|Robot experiments"  : "robot@robot",
            "exp1|robot-proglist|Robot experiments"  : "robot@robot",
            "exp1|robot-maze|Robot experiments"      : "robot-maze@robot-maze",
            "exp1|robotarm|Robot experiments"        : "robotarm@robotarm",
            "exp1|submarine|Submarine experiments"   : "submarine@submarine",
            "exp1|aquarium|Aquatic experiments"      : "submarine@submarine",
            "exp1|aquariumjs|Aquatic experiments"    : "submarine@submarine",
            "exp1|submarinejs|Aquatic experiments"   : "submarine@submarine",
            "exp1|romie|Robot experiments"           : "romie@romie",
            "exp1|romie_labpsico|Robot experiments"  : "romie@romie",
            "exp1|romie_demo|Robot experiments"      : "romie@romie",
            "exp1|romie_blockly|Robot experiments"   : "romie@romie",
            "exp1|archimedes|Aquatic experiments"    : "archimedes@archimedes",
            "exp1|elevator|FPGA experiments"         : "elevator@elevator",
            "exp1|unr-physics|Physics experiments"   : "unr@unr",
            "exp1|blink-led|LabVIEW experiments"     : "labview@labview",
            "exp1|ud-pic18|PIC experiments"          : "pic18@pic18",
            "exp1|binary|Games"                      : "binary@binary",
            "exp1|control-app|Control experiments"   : "control@control",
            "exp1|incubator|Farm experiments"        : "incubator@incubator",
            "exp1|new_incubator|Farm experiments"    : "new_incubator@new_incubator",
            "exp1|http|HTTP experiments"             : "http1@http",
        }
}

core_coordinator_external_servers = {
    'microelectronics@iLab experiments'  : [ 'microelectronics_external' ],
#    'robot-movement@Robot experiments'   : [ 'robot_external' ],
    'external-robot-movement@Robot experiments'   : [ 'robot_external' ],
    'ud-logic@PIC experiments'           : [ 'logic_external' ],
}

ilab_microelectronics = ("ILAB_BATCH_QUEUE", {
    'lab_server_url' : 'http://weblab2.mit.edu/services/WebLabService.asmx',
    'identifier'     : '',
    'passkey'        : '',
})

weblabdeusto_federation_demo = ("EXTERNAL_WEBLAB_DEUSTO", {
    'baseurl' : 'http://weblab.deusto.es/weblab/',
    'username' : 'weblabfed',
    'password' : 'password',
    'experiments_map' : {'external-robot-movement@Robot experiments' : 'robot-movement@Robot experiments'}
})

core_scheduling_systems = {
        "microelectronics_external" : ilab_microelectronics,
        "robot_external"            : weblabdeusto_federation_demo,
        "logic_external"            : weblabdeusto_federation_demo,
        "fpga"        : ("PRIORITY_QUEUE", {}),
        "pld"         : ("PRIORITY_QUEUE", {}),
        "gpib"        : ("PRIORITY_QUEUE", {}),
        "dummy"       : ("PRIORITY_QUEUE", {}),
        "dummy-batch" : ("PRIORITY_QUEUE", {}),
        "logic"       : ("PRIORITY_QUEUE", {}),
        "flashdummy"  : ("PRIORITY_QUEUE", {}),
        "javadummy"   : ("PRIORITY_QUEUE", {}),
        "jsdummy"     : ("PRIORITY_QUEUE", {}),
        "jsfpga"      : ("PRIORITY_QUEUE", {}),
        "visir"       : ("PRIORITY_QUEUE", {}),
        "vm"          : ("PRIORITY_QUEUE", {}),
        "vm-win"      : ("PRIORITY_QUEUE", {}),
        "robot"       : ("PRIORITY_QUEUE", {}),
        "robotarm"    : ("PRIORITY_QUEUE", {}),
        "submarine"   : ("PRIORITY_QUEUE", {}),
        "romie"       : ("PRIORITY_QUEUE", {}),
        "archimedes"  : ("PRIORITY_QUEUE", {}),
        "elevator"    : ("PRIORITY_QUEUE", {}),
        "labview"     : ("PRIORITY_QUEUE", {}),
        "pic18"       : ("PRIORITY_QUEUE", {}),
        "binary"      : ("PRIORITY_QUEUE", {}),
        "unr"         : ("PRIORITY_QUEUE", {}),
        "control"     : ("PRIORITY_QUEUE", {}),
        "incubator"   : ("PRIORITY_QUEUE", {}),
        "new_incubator"   : ("PRIORITY_QUEUE", {}),
        "robot-maze"  : ("PRIORITY_QUEUE", {}),
        "http"  : ("PRIORITY_QUEUE", {}),
    }

core_universal_identifier       = 'da2579d6-e3b2-11e0-a66a-00216a5807c8'
core_universal_identifier_human = 'server at university X'

core_server_url = 'http://localhost/weblab/'

#####################################
# Login Server Facade configuration #
#####################################


#######################################
# Login Server Database configuration #
#######################################

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

uned_sso = True
