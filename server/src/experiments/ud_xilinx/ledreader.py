#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
#

import urllib
import cStringIO
import PIL
from PIL import Image
import colorsys


class LedReader(object):
    
    def __init__(self, url):
        self._url = url
        
    def irgb_to_frgb(self, p):
        return p[0] / 255., p[1] / 255., p[2] / 255.
        
    def irgb_to_hls(self, p):
        p = self.irgb_to_frgb
        return colorsys.rgb_to_hsv(p)
        
        
    def read(self):
        file = cStringIO.StringIO(urllib.urlopen(self._url).read())
        img = Image.open(file)
        rgbim = img.convert('RGB')
        pix = rgbim.load()
        
        print "Size: ", rgbim.size[0], " ", rgbim.size[1]
        
        # Turn reds blue for testing.
        for x in xrange(0, rgbim.size[0]):
            for y in xrange(0, rgbim.size[1]):
                p = pix[x, y]
                inv = p
                p = self.irgb_to_frgb(p)
                if p[0] < 0.1 or p[0] > 0.9: # RED HUE
                    if p[1] > 0.3: # Approx saturation
                        if p[2] > 0.8 and p[2] < 1:
                            print "inv"
                            pix[x, y] = 0, 255, 0
               
        rgbim.show()        
        
        
    def __str__(self):
        return "00"


if __name__ == '__main__':
    lr = LedReader("http://upload.wikimedia.org/wikipedia/commons/5/54/ALTERA_DE2_FPGA_Board.jpg")
    
    while(True):
        try:
            lr.read()
        except IOError:
            print "Err"
        else:
            break
    print str(lr)