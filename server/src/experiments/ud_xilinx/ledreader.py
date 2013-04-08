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
    
    LED_DIAMETER = 10
    LED_DIAMETER_EXTRA = 5
    LED_LIT_PIXEL_THRESHOLD = 35
    
    def __init__(self, url):
        self._url = url
        self._leds = [ (111, 140), (139, 140), (167, 140), (194, 140), (223, 140), (247, 139) ]
        
    def irgb_to_frgb(self, p):
        return p[0] / 255., p[1] / 255., p[2] / 255.
        
    def irgb_to_hls(self, p):
        p = self.irgb_to_frgb
        return colorsys.rgb_to_hsv(p)
    
    def is_led_red(self, p):
        if p[0] < 0.1 or p[0] > 0.9: # RED HUE
            if p[1] > 0.3: # Approx saturation
                if p[2] > 0.8 and p[2] <= 1:
                    return True
                
    def count_led_red_in_sq(self, pix, size, center, distance):
        cx = center[0]
        cy = center[1]
        
        xstart = cx - distance/2
        if xstart < 0: xstart = 0
        
        xend = cx + distance/2
        if xend >= size[0]: xend = size[0]-1
        
        ystart = cy - distance/2
        if ystart < 0: ystart = 0
        
        yend = cy + distance/2
        if yend >= size[1]: yend = size[1]-1 
        
        count = 0
        for x in xrange(xstart, xend+1):
            for y in xrange(ystart, yend+1):
                #print x, y, pix[x, y]
                if self.is_led_red(self.irgb_to_frgb(pix[x, y])):
                    count += 1
        
        return count
    
    def test(self):
        
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
                if self.is_led_red(p):
                    print "inv"
                    pix[x, y] = 0, 255, 0
                    
        rgbim.show()
        
        
        
    def read(self):
        file = cStringIO.StringIO(urllib.urlopen(self._url).read())
        img = Image.open(file)
        rgbim = img.convert('RGB')
        pix = rgbim.load()
        
        print "Size: ", rgbim.size[0], " ", rgbim.size[1]
        
        for led in self._leds:
            count = self.count_led_red_in_sq(pix, rgbim.size, led, self.LED_DIAMETER + self.LED_DIAMETER_EXTRA)
            print (count > self.LED_LIT_PIXEL_THRESHOLD), "(", count, ")"
               
        rgbim.show()        
        
        
    def __str__(self):
        return "00"

# PLD LED positions

if __name__ == '__main__':
    lr = LedReader("https://www.weblab.deusto.es/webcam/proxied/pld1?1696782330")
    
    while(True):
        try:
            lr.read()
        except IOError:
            print "Err"
        else:
            break
    print str(lr)