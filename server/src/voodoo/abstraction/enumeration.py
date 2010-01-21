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
#                                                                                            #
#                 See enumeration_examples.py for examples                                   #
#                                                                                            #
##############################################################################################

##############################################################################################
#                                                                                            #
#                                   Enumeration generator                                    #
#                                                                                            #
##############################################################################################

def _enum_reconstructor(modulename, name):
    import sys
    return getattr(sys.modules[modulename],name)

def __generate_isWhatever(NewClass):
    def __isWhatever(variable,par = None):
        """
            It will check if the instance that is passed is of the same 
            class of the dynamically generated enumeration type
        """
        if par is None:
            return variable.__class__ == NewClass
        else:
            return par.__class__ == NewClass
    return __isWhatever

def __generate_getValues(values):
    def __getValues(par=None):
        """
            It will give us a list with all the possible elements of an 
            enumeration.
        """
        return values
    return __getValues

def __generate_getEnumerated(values):
    def __getEnumerated(name):
        """
            It will give us the enumerated value for "name"
        """
        possible_value = [ i for i in values if i.name == name ]
        if len(possible_value) == 1:
            return possible_value[0]
        elif len(possible_value) == 0:
            raise NameError('Not a valid attribute: %s' % name)
        else:
            raise ValueError('Not a valid state: too many values for %s' % name)
    return __getEnumerated

class EnumerationBase(object):
    def __init__(self):
        super(EnumerationBase,self).__init__()

class EnumerationException(Exception):
    def __init__(self,*args,**kargs):
        Exception.__init__(self,*args,**kargs)

def inspectEnumeration(enumeration):
    returnValue = {}
    module_name = enumeration._module_name
    enum_name = module_name[module_name.rfind('.')+1:]
    module = __import__(module_name,globals(),locals(),[''])
    returnValue['getValues'] = getattr(module,'get' + enum_name + 'Values')
    returnValue['is'] = getattr(module,'is' + enum_name)
    returnValue['getEnumerated'] = getattr(module,'get' + enum_name + 'Enumerated')
    returnValue['name'] = enum_name
    returnValue['module'] = module
    return returnValue

def gen(module,items,name,delete_rest_of_module=False):
    """
        Generates a new enumeration.
        
        "module"            -> module or class where the enumeration should be 
        
        "items"             -> possible values of each enumeration
        
        "name"              -> the name of the enumeration
        
        "delete_rest_of_module"     -> if this option is True, it will delete the rest
                        of the module. By default, it will not do it. It's
                        useful if you want to "clean" the module
                        
        The function doesn't return any value. 
        
        It will modify the "module" module or class, adding instances of a new dynamically 
        generated type. The type itself will not be available, although it will be accessible 
        through the __class__ attribute of the instances. The instances will not be compared 
        with instances of other enumerations. The module will also have two methods called:
    
        getValues(), which will return all the possible values of the module
        
        is<NameOfEnumeration>, which will return if the parameter is an instance of the Enumeration
        or not.
    """
    if delete_rest_of_module:
        for i in [i for i in dir(module) if not i.startswith('_')]:
            delattr(module,i)
    class EnumerationClass(EnumerationBase):
        def __init__(self,number,items,classname,name):
            super(EnumerationClass,self).__init__()
            if number in range(len(items)):
                self.__number = number
                self.__classname = classname
                self.name = name
            else:
                raise EnumerationException('%i not recognized in %s' % (number,name) )
        def __reduce__(self):
            return (_enum_reconstructor,(self._module_name,self.name))
        def __cmp__(self,par):
            if par == None:
                return 1
            elif par.__class__ != self.__class__:
                raise EnumerationException('%s not a %s' % (par,self.__classname))
            else:
                return cmp(self.__number,par.__number)
        def __eq__(self, other):
            return self.__cmp__(other) == 0
        def __repr__(self):
            return "<%s enumeration: %s>" % (self.__classname, self.name)

    import new

    NewClass = new.classobj(name,(EnumerationClass,),{})

    values=[]
    for i in items:
        instance = NewClass(items.index(i),items,name,i)
        setattr(module,i,instance)
        values.append(instance)
    
    values = tuple(values)
    
    def new_init(self):
        raise ValueError("No more instances of %s allowed" % name)
    NewClass.__init__ = new_init

    setattr( module, '_enumeration_name', name )
   
    isWhatever = __generate_isWhatever(NewClass)
    isWhatever.func_name = 'is' + name
    setattr( module, 'is'+name, isWhatever )

    getValues = __generate_getValues(values)
    getValues.func_name = 'get' + name + 'Values'
    setattr( module, 'get' + name + 'Values', getValues )

    getEnumerated = __generate_getEnumerated(values)
    getEnumerated.func_name = 'get' + name + 'Enumerated'
    setattr( module, 'get' + name + 'Enumerated', getEnumerated)

    setattr(module,name,NewClass)
    NewClass._module_name = module.__name__
    NewClass._module      = module

