##################################
# Laboratory Server configuration #
##################################

laboratory_session_type = 'Memory'

laboratory_assigned_experiments = {
        'exp1:ud-dummy@Dummy experiments':
            {
                 'coord_address': 'experiment_dummy:dummy_instance@main_machine',
                 'checkers': ()
            },
        'exp1:javadummy@Dummy experiments':
            {
                 'coord_address': 'experiment_javadummy:main_instance@main_machine',
                 'checkers': ()
            },
    }
