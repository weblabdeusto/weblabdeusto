#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

fake_controller = True
# fake_controller = False
verbose_controller = True

number_of_lights   = 3
if fake_controller:
    controller_address = '127.0.0.1'
else:
    controller_address = '192.168.0.110:8000'

historic_directory = 'incubator_historic'

cams = [
    'http://www.weblab.deusto.es/webcam/proxied.py/egg1',
    'http://www.weblab.deusto.es/webcam/proxied.py/egg2',
    'http://www.weblab.deusto.es/webcam/proxied.py/egg3'
]

fake_images = fake_controller and False
if fake_images:
    cams = [
        'http://127.0.0.1:8888/weblabclientlab//img/udeusto-logo.jpg',
        'http://127.0.0.1:8888/weblabclientlab//img/udeusto-logo.jpg',
        'http://127.0.0.1:8888/weblabclientlab//img/udeusto-logo.jpg',
    ]

webcams_info = [ 
    { # '1'
        'webcam_url'   : cams[0],
        'mjpeg_url'    : 'http://www.weblab.deusto.es/webcam/egg1/video.mjpeg',
        'mjpeg_width'  : 320,
        'mjpeg_height' : 240,
    },
    { # '2'
        'webcam_url' : cams[1],
        'mjpeg_url'    : 'http://www.weblab.deusto.es/webcam/egg2/video.mjpeg',
        'mjpeg_width'  : 320,
        'mjpeg_height' : 240, 
    },
    { # '3'
        'webcam_url' : cams[2],
        'mjpeg_url'    : 'http://www.weblab.deusto.es/webcam/egg3/video.mjpeg',
        'mjpeg_width'  : 320,
        'mjpeg_height' : 240,
    }, 
]

import os
if not os.path.exists(historic_directory):
    os.mkdir(historic_directory)

