#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

fake_controller = True

number_of_lights   = 3
controller_address = '127.0.0.1'

historic_directory = 'incubator_historic'

webcams_info = [ 
    { # '1'
        'webcam_url' : 'http://www.weblab.deusto.es/webcam/proxied.py/robot1',
    },
    { # '2'
        'webcam_url' : 'http://www.weblab.deusto.es/webcam/proxied.py/pld1',
    },
    { # '3'
        'webcam_url' : 'http://www.weblab.deusto.es/webcam/proxied.py/fishtank1',
    }, 
]

import os
if not os.path.exists(historic_directory):
    os.mkdir(historic_directory)

