#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

submarine_pic_location = 'http://192.168.0.90/'

thermometer_path = '../../../client/war/weblabclientlab/img/experiments/submarine-thermometer.png'

webcams_info = [
    dict(
        webcam_url             = 'http://www.weblab.deusto.es/webcam/proxied.py/fishtank1',
        mjpeg_url              = 'http://www.weblab.deusto.es/webcam/fishtank1/video.mjpeg',
        mjpeg_width            = 320,
        mjpeg_height           = 240,
    ),
    dict(
        webcam_url             = 'http://www.weblab.deusto.es/webcam/proxied.py/fishtank2',
        mjpeg_url              = 'http://www.weblab.deusto.es/webcam/fishtank2/video.mjpeg',
        mjpeg_width            = 320,
        mjpeg_height           = 240,
    ),
]

real_device = False

