#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
# 

##############################################################################################
#                                                                                            #
#             Copyright:     (c) 2006 Pablo Orduña <pablo@ordunya.com>                       #
#             LICENSE:       MIT License ( http://pablo.ordunya.com/license-mit )            #
#                                                                                            #
##############################################################################################


if __name__ != '__main__':
    raise RuntimeError("module %s should never be imported, it's just an examples file" % __name__)

import voodoo.abstraction.checker as checker

def myFunction(par1,par2,par3):
    checker.check_types((par1,par2,par3),(int,str,dict))
    print 'par1 is a int with value %i' % par1
    print 'par2 is a dict with value %s' % par2
    print 'par3 is a dict with value %s' % str(par3)
    

print "Calling myFunction(1,'hello',{})"
myFunction(1,'hello',{})
print 'done'

print
print

print "Calling myFunction('hello',1,{})"
try:
    myFunction('hello',1,{})
except Exception, e:
    print e,'\t',e.__class__

print
print

def handler(errors):
    message = 'Controlled TypeError checking parameters. '
    for i in errors:
        message += "\nThe value of parameter number '%i' is '%s', and was suppossed to be a '%s'" % (i,str(errors[i][0]),str(errors[i][1]))
    print message
    print 'I should raise an exception because I know that my code will not be correctly executed'
    print 'I keep running anyway...'
    print

def myFunction2(par1,par2,par3):
    checker.check_types((par1,par2,par3),(int,str,dict),handler)
    print 'par1 is a int with value %i' % par1
    print 'par2 is a dict with value %s' % par2
    print 'par3 is a dict with value %s' % str(par3)


print "Calling myFunction('hello',1,{})"

try:
    myFunction2('hello',1,{})
except Exception, e:
    print e,'\t', e.__class__

print
print

#Checking None Values
def checkingNoneValues(par1, par2, par3):
    print "Checking par1 and par2...\t\t\t\t",
    checker.check_none((par1,par2))
    print "done"
    print "Checking par1, par2 and par3, but only the first two...\t",
    checker.check_none((par1,par2,par3),(True,True,False))
    print "done"
    print "Checking par1, par2 and par3...\t\t\t"
    try:
        checker.check_none((par1,par2,par3))
    except Exception, e:
        print e,'\t',e.__class__
        
checkingNoneValues('a','b',None)

print 
print 


def checkingValues(par1, par2):
    checker.check_values((par1,par2),(lambda x : x >= 0,lambda x : x <= 0))
    print 'par1 is lower than 0 and par2 is higher than 0'

print 'par1 = -1; par2 = 2...'
checkingValues(-1,2)
print 'par1 = 2; par2 = -1...'
checkingValues(2,1)
