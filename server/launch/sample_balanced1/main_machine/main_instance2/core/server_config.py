##############################
# RemoteFacade configuration #
##############################

core_facade_soap_bind       = ''
core_facade_soap_port         = 20123
core_facade_soap_service_name = '/weblab/soap/'

core_facade_xmlrpc_bind    = ''
core_facade_xmlrpc_port      = 29345

core_facade_json_bind      = ''
core_facade_json_port        = 28345

admin_facade_json_port        = 28545

core_facade_server_route     = 'route2'

core_scheduling_systems = {
        "ud-fpga@FPGA experiments"     : ("PRIORITY_QUEUE", {}),
        "ud-pld@PLD experiments"       : ("PRIORITY_QUEUE", {}),
        "ud-gpib@GPIB experiments"     : ("PRIORITY_QUEUE", {}),
        "ud-pic@PIC experiments"       : ("PRIORITY_QUEUE", {}),
        "ud-dummy@Dummy experiments"   : ("PRIORITY_QUEUE", {}),
        "ud-logic@PIC experiments"     : ("PRIORITY_QUEUE", {}),
        "flashdummy@Dummy experiments" : ("PRIORITY_QUEUE", {}),
        "javadummy@Dummy experiments"  : ("PRIORITY_QUEUE", {}),
        "visirtest@Dummy experiments"  : ("PRIORITY_QUEUE", {}),
    }

core_coordinator_clean = False
core_web_facade_port = 29745
