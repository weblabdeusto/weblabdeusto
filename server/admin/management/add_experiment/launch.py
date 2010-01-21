#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

import sys

try:
    from configuration import DATABASE_NAME, CREATE_EXPERIMENT_CATEGORY, EXPERIMENT_CATEGORY_NAME, EXPERIMENT_OWNER_NAME, EXPERIMENT_NAME
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)


PRE_SQL = """-- This file should be run under admin privileges

use %(database_name)s;

START TRANSACTION;
"""

INSERT_EXPERIMENT_CATEGORY_SQL = """
INSERT INTO wl_v_a_rw_ExperimentCategory(
    experiment_category_name
    ) VALUES (
        '%(experiment_category_name)s'
        );
"""

INSERT_EXPERIMENT_SQL = """
INSERT INTO wl_v_a_rw_Experiment(
    experiment_owner_id,
    experiment_category_id,
    experiment_start_date,
    experiment_end_date,
    experiment_name
    ) VALUES (
       GetUserIDByName('%(experiment_owner_name)s'),
       GetExperimentCategoryIDByName('%(experiment_category_name)s'),
       CURDATE(),
       ADDDATE(CURDATE(), INTERVAL 10 YEAR),
       '%(experiment_name)s'
 );
"""

POST_SQL = """
COMMIT;
"""

sql_code = PRE_SQL % {
                'database_name': DATABASE_NAME
                }

if CREATE_EXPERIMENT_CATEGORY:
    sql_code += INSERT_EXPERIMENT_CATEGORY_SQL % {
                    'experiment_category_name': EXPERIMENT_CATEGORY_NAME
                    }    

sql_code += INSERT_EXPERIMENT_SQL % {
                'experiment_owner_name': EXPERIMENT_OWNER_NAME,
                'experiment_category_name': EXPERIMENT_CATEGORY_NAME,
                'experiment_name': EXPERIMENT_NAME
                }    

sql_code += POST_SQL

filename = 'output.%s.sql' % EXPERIMENT_NAME

open(filename,'w').write(sql_code)

print "File %s successfully created. Now mysql -uUSERNAME -p < %s" % (filename,filename)