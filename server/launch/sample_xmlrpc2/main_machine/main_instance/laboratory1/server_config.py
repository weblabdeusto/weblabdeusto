##################################
# Laboratory Server configuration #
##################################

laboratory_session_type = 'Memory'

laboratory_assigned_experiments = [
        'exp1|ud-fpga|FPGA experiments;experiment_fpga:main_instance@main_machine',
        'exp1|ud-pld|PLD experiments;experiment_pld:main_instance@main_machine',
        'exp1|ud-dummy|Dummy experiments;experiment_dummy:main_instance@main_machine',
        'exp2|ud-dummy|Dummy experiments;experiment_dummy:dummy_instance@main_machine',
    ]


