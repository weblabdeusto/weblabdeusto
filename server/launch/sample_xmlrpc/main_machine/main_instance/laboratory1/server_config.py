##################################
# Laboratory Server configuration #
##################################

laboratory_session_type = 'Memory'

laboratory_assigned_experiments = {
        'exp1:ud-pic@PIC experiments':
            {
                 'coord_address': 'experiment_pic:pic_instance@main_machine',
                 'checkers': ()
            },
        'exp1:ud-pic2@PIC experiments':
            {
                 'coord_address': 'experiment_pic2:pic_instance@main_machine',
                 'checkers': ()
            },
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
