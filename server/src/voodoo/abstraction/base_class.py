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
#                 See abstract_class_generator_examples.py for examples                      #
#                                                                                            #
##############################################################################################

# import voodoo.abstraction.abstract_class_generator as abstract_class_generator
# 
# def __collect_methods(classType):
#   data = {}
#   for i in [ i for i in dir(classType) if hasattr(i,'__call__') ]:
#       data[i] = [ (classType, getattr(classType,i)) ]
#   for i in classType.__bases__:
#       data_inherited = __collect_methods(i)
#       for j in data_inherited:
#           if data.has_key(j):
#               for k in data_inherited[j]:
#                   data[j].append(k)
#           else:
#               data[j] = data_inherited[j]
#   return data
# 
# def __isAbstractClassType(classType):
#   if issubclass(classType,abstract_class_generator.__DEEPEST_CLASS):
#       if classType == abstract_class_generator.__DEEPEST_CLASS or \
#           abstract_class_generator.__DEEPEST_CLASS in classType.__bases__:
#           return True
#       for i in classType.__bases__:
#           if __DEEPEST_CLASS in i.__bases__:
#               return True
#   return False
#       
# def __isAbstractMethod(classType,functionName):
#   if __isAbstractClassType(classType):
#       return functionName in classType.mustInheritMethods
#   return False
#   
# class BaseClass:
#   def __init__(self):
#       #all_methods is a dictionary like:
#       #{ functionName : [(classType,function)] }
#       all_methods = collect_methods(self.__class__)
#       methods_with_conflicts = []
#       for i in all_methods:
#           #i is functionName
#           #all_methods[i] is a list like [(classType,function)]
#           not_abstract_methods_with_same_name = [ j for j in all_methods[i] if not __isAbstractMethod(j[0],i) ]
#           #not_abstract_methods_with_same_name is a list like:
#           #[ (classType, function) ], with all the not abstract 
#           #functions associated to the name "i" in the bases
#           
#           #if the number of functions is superior to 1
#           if len(not_abstract_methods_with_same_name) > 1:
#               
#               #now we have to check if, between these methods, some methods are just
#               #overriding others, or not.
#               
#               #conflicts_of_this_method is a dictionary like:
#               #{ classTypeA : {classTypeB : {}, classTypeC : { classTypeD : {} } }, classTypeE : {}}
#               #if self.__class__ is subclass of classTypeA and classTypeE,
#               #and classTypeA is subclass of classTypeB and classTypeC
#               #and classTypeC is subclass of classTypeD
#               conflicts_of_this_method = {}
# 
#               #j is each (classType,function)
#               for j in not_abstract_methods_with_same_name:
#                   
#                   for k in not_abstract_methods_with_same_name:
#                       
#                       if j != j:
#                           if issubclass(j[0],k[0]):
#                               #j is just overriding k
                                

# def __collect_methods(classType):
#   data = {}
#   for i in [ i for i in dir(classType) if hasattr(i,'__call__') ]:
#       #i is every single method that classType has, even if it's inherited
#       #so let's just add it if it's not inherited
#       addFunction = True
#       for j in classType.__bases__:
#           if getattr(classType,i) == getattr(j,i):
#               addFunction = False
#       #addFunction says if this function is not inherited, so should be added
#       if addFunction:
#           #it's the first class having this function, so:
#           data[i] = {classType : {}}
#   #now we have added every new function of this class. Let's get every function inherited now
#   for i in classType.__bases__:
#       new_data = __collect_methods(i)
#       #new_data is a dictionary like:
#       #{ function : {classA : {classB : {} }, classC : {} } }
#       __add_data(new_data,data)
#   return data
# 
# def __add_data(new_data, data):
#   """ 
#       Stores information stored in "new_data" into "data".
#       If data was:
#       { functionName1 : { classA : { classB : {} } }, functionName2 : { classC : {} }}
#       and new_data was:
#       { functionName2 : { classD : {} }, functionName3 : { classE : {classF : {}}}}
#       data should be, in the end:
#       { functionName1 : { classA : { classB : {} } }, functionName2 : { classC : { classD : {}} }, functionName3 : { classE : {classF : {}}}}
#       because if a functionName is already in data, 
#   """
#   pass
# 
# class BaseClass:
#   def __init__(self):
#       all_methods = __collect_methods(self.__class__)
#       #all_methods is a dictionary like:
#       #{ functionName1 : { classA : {} }, 
#       #   functionName2 : { classB : {classA : {}, classC : { classD : {}}}, 
#       #   functionName3 : {myClass : {} }}

def __collect_methods(classType):
    #I want to return a dictionary like:
    #{ functionName : [classA, classB, classC] }
    #being classType subclass of classA, classB and classC,
    #being functionName in all these classes, and being different in each class
    pass
