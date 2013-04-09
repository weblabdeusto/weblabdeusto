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
import time
import PIL
from PIL import Image
import colorsys


class LedReader(object):
    
    def __init__(self, url, leds, led_diameter, led_threshold):
        self._url = url
        self._leds = leds
        self._led_diameter = led_diameter
        self._led_threshold = led_threshold
        
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
        
        #print "Size: ", rgbim.size[0], " ", rgbim.size[1]
        
        # Turn reds blue for testing.
        for x in xrange(0, rgbim.size[0]):
            for y in xrange(0, rgbim.size[1]):
                p = pix[x, y]
                inv = p
                p = self.irgb_to_frgb(p)
                if self.is_led_red(p):
                    print "inv"
                    pix[x, y] = 0, 255, 0
                    
        #rgbim.show()
        
        
        
    def read(self, ret_count = False):
        """
        read(ret_count = False)
        
        Tries to read the state of the LEDs.
        Throws an exception on failure.
        
        @param ret_count If true, the list returned will contain when the
        LED is turned on a count of "lit" pixels. If false, it will simply
        return '1'.
        
        @return Returns a list containing the state of each LED. The 
        state will be '0' if the LED is off, and '1' or a
        higher-than-the-threshold count if it is on.
        """
        f = cStringIO.StringIO(urllib.urlopen(self._url).read())
        img = Image.open(f)
        rgbim = img.convert('RGB')
        pix = rgbim.load()
        
        #print "Size: ", rgbim.size[0], " ", rgbim.size[1]
        
        states = []
        
        for led in self._leds:
            count = self.count_led_red_in_sq(pix, rgbim.size, led, self._led_diameter)
            if count > self._led_threshold:
                if ret_count: states.append(count)
                else: states.append('1')
            else:
                states.append('0')
        
        return states    
        
        
    def __str__(self):
        return "LedReader"
    
    
    def read_times(self, times):
        """
        read_times(times)
        Tries to read the state of the LEDs the specified number of times.
        Each attempt takes around a second.
        @param times Number of times it tries to read the led state. Should be higher than 0.
        @return List with the value of each LED.
        """
        errcount = 0
        while(True):
            try:
                return lr.read()
            except IOError:
                errcount += 1
            if errcount >= times:
                raise 
            time.sleep(1)

# PLD LED positions

if __name__ == '__main__':
    pld_leds = [ (111, 140), (139, 140), (167, 140), (194, 140), (223, 140), (247, 139) ]
    fpga_leds = [ (84, 192), (92, 192), (101, 192), (111, 192), (120, 192), (128, 192), (138, 192), (147, 192) ]
    fpga = "https://www.weblab.deusto.es/webcam/proxied.py/fpga1?-665135651"
    pld = "https://www.weblab.deusto.es/webcam/proxied/pld1?1696782330"
    lr = LedReader(fpga, fpga_leds, 5, 7)
    
    while(True):
        try:
            print lr.read_times(5)
        except IOError:
            print "Err"
        time.sleep(1)
            
    print str(lr)