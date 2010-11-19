##################################
# Laboratory Server configuration #
##################################

laboratory_assigned_experiments = {
        'exp1:ud-fpga@FPGA experiments':
            {
                 'coord_address': 'experiment_fpga:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:ud-pld@PLD experiments':
            {
                 'coord_address': 'experiment_pld:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:ud-gpib@GPIB experiments':
            {
                 'coord_address': 'experiment_gpib:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:ud-pic@PIC experiments':
            {
                 'coord_address': 'experiment_pic:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:ud-dummy@Dummy experiments':
            {
                 'coord_address': 'experiment_dummy:main_instance@main_machine',
                 'checkers': ()
            },
        'exp2:ud-dummy@Dummy experiments':
            {
                 'coord_address': 'experiment_dummy:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:ud-logic@PIC experiments':
            {
                 'coord_address': 'experiment_logic:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:flashdummy@Dummy experiments':
            {
                 'coord_address': 'experiment_flashdummy:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:javadummy@Dummy experiments':
            {
                 'coord_address': 'experiment_javadummy:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:visirtest@Dummy experiments':
            {
                 'coord_address': 'experiment_testvisir:main_instance@main_machine',
                 'checkers': ()
            },
        'exp1:vm@Dummy experiments':
            {
                 'coord_address': 'experiment_vm:main_instance@main_machine',
                 'checkers': ()
            }
    }