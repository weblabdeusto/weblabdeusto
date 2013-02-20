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


import subprocess
import os
import base64
import time


UCF_INTERNAL_CLOCK = "fpga_clock_internal.ucf"
UCF_WEBLAB_CLOCK = "fpga_clock_weblab.ucf"
UCF_BUTTON_CLOCK = "fpga_clock_but3.ucf"
UCF_SWITCH_CLOCK = "fpga_clock_swi9.ucf"

ENABLE_LOG_FILE = True
LOG_FILE = "compiler.log"

DEFAULT_UCF = UCF_INTERNAL_CLOCK


class Compiler(object):
    
    BASE_PATH = ".." + os.sep + ".." + os.sep + "experiments" + os.sep + "xilinxc" + os.sep + "files"
    DEBUG = False
    
    def __init__(self, filespath = BASE_PATH, toolspath = ""):
        """
        Constructs a new Compiler object.
        @param filespath Path to the Xilinx base project and VHD/UCF files.
        @param toolspath Path to the Xilinx command line tools (xst, par, etc). If those are in the 
        path, this may be blank.
        """
        self.filespath = filespath
        self.toolspath = toolspath
        if self.toolspath != "":
            self.toolspath += os.sep
        self.errorlines = []
        
        # The following will be used to measure compileit's time.
        self._synt_start = None
        self._synt_elapsed = None
            
        # By default, we will use this UCF.
        self.ucf = DEFAULT_UCF
        
        if(ENABLE_LOG_FILE):
            # Load the logfile we will use to track the compiling process.
            self.logfile = open(self.filespath + os.sep + LOG_FILE, "w")
        else:
            self.logfile = None
            
        if(self.DEBUG):
            print "[Xilinxc Compiler]: Running from " + os.getcwd()
            
            
    def close(self):
        """
        Deallocates resources used by the Compiler class.
        """
        if(ENABLE_LOG_FILE):
            self.logfile.close()
            
            
    def choose_clock(self, vhdl):
        """
        Tries to find a special markup within the VHDL code to decide which UCF to use.
        @param vhdl The VHDL code.
        """
        if "@@@CLOCK:WEBLAB@@@" in vhdl:
            self.ucf = UCF_WEBLAB_CLOCK
        elif "@@@CLOCK:INTERNAL@@@" in vhdl:
            self.ucf = UCF_INTERNAL_CLOCK
        elif "@@@CLOCK:BUTTON@@@" in vhdl:
            self.ucf = UCF_BUTTON_CLOCK
        elif "@@@CLOCK:SWITCH@@@" in vhdl:
            self.ucf = UCF_SWITCH_CLOCK
        
            

    def feed_vhdl(self, vhdl, debugging = False):
        """
        Replaces the local vhdl file contents with the provided code.
        Warning: It will replace the file contents.
        @param vhdl String containing the new VHDL code.
        """
        vhdlpath = self.filespath + os.sep + "base.vhd"
        if(debugging):
            print "[DBG]: Feed_vhdl pretending to replace %s with: " % (vhdlpath)
            print vhdl
        else:
            f = file(vhdlpath, "w")
            f.write(vhdl)
            f.close()
    
    def synthesize(self):
        process = subprocess.Popen([self.toolspath + "xst", "-intstyle", "ise", "-ifn", "base.xst", 
                                    "-ofn", "base.syr"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd = self.filespath)
        
        so, se = process.communicate()
        
        if ENABLE_LOG_FILE:
            self.logfile.write(so + "\n")
            self.logfile.write(se + "\n")
        
        if(self.DEBUG):
            print so, se
        
        if len(se) > 0 or "ERROR:" in so:
            
            if(len(se) > 0):
                self.errorlines.append(se + "\n")
            
            try:
                errors_start = so.index("ERROR:HDLParsers")
                errors_end = so.index("-->")
                errors_str = so[errors_start:errors_end]
                self.errorlines.append(errors_str)
            except:
                pass
            
            return False
        
        return True
    
    def ngdbuild(self):
        process = subprocess.Popen([self.toolspath + "ngdbuild", "-intstyle", "ise", "-dd", "_ngo", "-nt", "timestamp", "-uc", self.ucf, 
                                    "-p", "xc3s1000-ft256-4", "base.ngc", "base.ngd"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd = self.filespath)

        so, se = process.communicate()
        
        if ENABLE_LOG_FILE:
            self.logfile.write(so + "\n")
            self.logfile.write(se + "\n")
        
        if(self.DEBUG): 
            print so, se

        if len(se) == 0 and "NGDBUILD done." in so:
            return True
        
        try:
            errors_start = so.index("ERROR:")
            errors_end = so.index("Done...")
            errors_str = so[errors_start:errors_end]
            self.errorlines.append(errors_str)
        except:
            pass
        
        return False
    
    def mapping(self):
        process = subprocess.Popen([self.toolspath + "map", "-intstyle", "ise", "-p", "xc3s1000-ft256-4", 
                                    "-cm", "area", "-ir", "off", "-pr", "off", "-c", "100", 
                                    "-o", "base_map.ncd", "base.ngd", "base.pcf"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd = self.filespath)
        
        so, se = process.communicate()
        
        if ENABLE_LOG_FILE:
            self.logfile.write(so + "\n");
            self.logfile.write(se + "\n");
        
        if(self.DEBUG):
            print so, se
        
        if len(se) == 0 and "Mapping completed." in so:
            return True
        
        return False;
        
    def par(self):
        process = subprocess.Popen([self.toolspath + "par", "-w", "-intstyle", "ise", "-ol", "high", "-t", "1",
                                    "base_map.ncd", "base.ncd", "base.pcf"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd = self.filespath)
        
        so, se = process.communicate()
        
        if ENABLE_LOG_FILE:
            self.logfile.write(so + "\n");
            self.logfile.write(se + "\n");
        
        if(self.DEBUG):
            print so, se
        
        if len(se) == 0 and "PAR done!" in so:
            return True
        
        return False
    
    def implement(self):
        result = self.ngdbuild()
        if(result):
            result = self.mapping()
            if(result):
                result = self.par()
                return result
        return False
    
    def retrieve_bitfile(self):
        """
        Retrieves the last bitfile generated, as a b64 string. Note that if you previously
        tried to generate a bitstream file but it failed, then the wrong bitfile will most
        likely be returned.
        """
        f = file(self.filespath + os.sep + "base.bit")
        contents = f.read()
        f.close()
        b64contents = base64.b64encode(contents)
        return b64contents
    
    def generate(self):
        process = subprocess.Popen([self.toolspath + "bitgen", "-intstyle", "ise", "-f", "base.ut", 
                                    "base.ncd", "-g", "StartUpClk:JtagClk"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd = self.filespath)
        
        # We use process.wait rather than process.communicate because
        # when bitgen is executed, WebTalk stays running in the background,
        # which causes an error. And there seems to be no way to disable it.
        
        r = process.wait()
        
        if ENABLE_LOG_FILE or self.DEBUG:
            outr = process.stdout.read()
            oute = process.stderr.read()
        
        if ENABLE_LOG_FILE:
            self.logfile.write(outr + "\n");
            self.logfile.write(oute + "\n");
        
        if(self.DEBUG):
            print outr
            print oute
        
        if(r == 0):
            return True
        
        return False
    
    def compileit(self): 
        # Track the time
        self._synt_start = time.time()
        
        # Read VHDL code to compile
        f = open(self.filespath + os.sep + "base.vhd", "r")
        vhdl = f.read()
        f.close()
        
        # Choose the right clock
        self.choose_clock(vhdl)
        
        result = self.synthesize() and self.implement() and self.generate()
    
        # Track time elapsed
        self._synt_elapsed = time.time() - self._synt_start
    
        return result
    
    def get_time_elapsed(self):
        """
        Returns the amount of seconds that the full "compiling" process took.
        That is, the time the "compileit" call took, even if it failed.
        @see compileit
        """
        return self._synt_elapsed
    
    def errors(self):
        """
        Returns a log of the errors that have occurred. Only certain types of errors
        are logged here. Note that the log is never cleared automatically.
        @see reset_errors
        """
        return ''.join(self.errorlines)
    
    def reset_errors(self):
        self.errorlines = []
    

if __name__ == "__main__":

    c = Compiler()
    
    c.DEBUG = True
    Compiler.DEBUG = True
    
    synt =  c.synthesize()
    if synt == False:
        print "REPORTING: "
        print c.errors()
        print "END OF REPORTING"
    
    else:
        imp = c.implement()
        if imp == False:
            print "REPORTING: "
            print c.errors()
            print "END OF REPORTING"
        print c.generate()
        #    print c.retrieve_bitfile()
    
    print "Good bye"