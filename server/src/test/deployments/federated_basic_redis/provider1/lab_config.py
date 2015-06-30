##################################
# Laboratory Server configuration #
##################################
from __future__ import print_function, unicode_literals

laboratory_assigned_experiments = {
        'exp1:dummy1@Dummy experiments':
            {
                 'coord_address': 'experiment_dummy1:main_instance@provider1_machine',
                 'checkers': ()
            },
        'exp1:dummy3_with_other_name@Dummy experiments':
            {
                 'coord_address': 'experiment_dummy3_with_other_name:main_instance@provider1_machine',
                 'checkers': ()
            },
    }
