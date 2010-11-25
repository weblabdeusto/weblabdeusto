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

def __generate_not_implemented_method(FunctionName):
    def __not_implemented_method(*arg,**karg):
        """
            All unimplemented methods will be replaced by this,
            being "FunctionName" the name of the function 
        """
        raise NotImplementedError(FunctionName)
    return __not_implemented_method

def __not_implemented(self,method):
    """
        Every abstract class will have a '_not_implemented' method which will
        raise a NotImplementedError Exception with the method name
    """
    raise NotImplementedError(method)

def _default_method_handler(methods):
    """
        This is the default behaviour for not implemented methods. 
        "methods" is a list of strings, being each string the name of
        an unimplemented method
    """
    raise NotImplementedError("Not implemented methods: %s" % methods)


def _default_abstract_handler(instance):
    """
        This is the default behaviour 
    """
    raise TypeError('Trying to instanciate %s, which is an abstract class' % instance.__class__)

class __DEEPEST_CLASS(object):
    """
        Every AbstractClass will inherit from this class
    """
    _abstract_handler = _default_abstract_handler


#One of the two public functions of this module
def AbstractClass(methods = [], name = "AbstractClass"):
    """
        This function creates Abstract Classes.
        
        This function will return a dynamically generated type class will have the unimplemented
        methods found in the list "methods" (with the corresponding documentation if it's a 
        dictionary), and which will be called "name".
        
        The constructor of the instances of this class will check for a "_abstract_handler" 
        method in order to call it if someone tries to instanciate the abstract class. If no 
        _abstract_handler is found, _default_abstract_handler will be called.
        
        The constructor of the instances of this class will call the method_handler passed as
        argument if method_handler is different to None with a list of unimplemented methods 
        as parameter.

        See abstract_class_examples.py for examples.
    """
    class NewAbstractClass(__DEEPEST_CLASS):
        def __init__(self, method_handler = _default_method_handler):
            """
                Every AbstractClass will have this as the constructor.
                
                It will check for a "_abstract_handler" method in order to call
                it if someone tries to instanciate the abstract class. If no 
                _abstract_handler is found, _default_abstract_handler will be
                called.
                
                It will call method_handler if method_handler is different to None
                with a list of unimplemented methods as parameter.
            """
            for i in self.__class__.__bases__:
                if i == NewAbstractClass:
                    self._abstract_handler()
           
            if method_handler != None:
                methodList = [
                        method 
                        for method in dir(self) 
                        if not isinstance(
                                getattr(self.__class__,method),
                                property
                        )   and hasattr(getattr(self, method),'__call__') 
                            and method in NewAbstractClass.mustInheritMethods
                    ]   
                cbac = self.__get_recursively_class_before_abstract(NewAbstractClass,self.__class__)
                methods = [ i for i in methodList if getattr(self.__class__,i) == getattr(NewAbstractClass,i) or getattr(self.__class__,i) == getattr(cbac,i)]
                if len(methods) > 0:
                    method_handler(methods)

        def __get_recursively_class_before_abstract(self, abstractClass, inheritedClass):
            """
                Auxiliar method
                Given a class "abstractClass", and a subclass of abstractClass "inheritedClass"
                This method will recursively look for the direct son of "abstractClass"
                
                Example:
                G is son of F and E
                E is son of D
                F is son of C and B
                C is son of A
                
                Calling __get_recursively_class_before_abstract(A,G) will return C
            """
            if issubclass(inheritedClass,abstractClass):
                for i in inheritedClass.__bases__:
                    if i == abstractClass:
                        return inheritedClass
                    ret_value = self.__get_recursively_class_before_abstract(abstractClass,i)
                    if ret_value != None:
                        return ret_value


    NewAbstractClass.__name__ = name
    my_methods = []
    for i in methods:
        my_methods.append(i)
        newFunc = __generate_not_implemented_method(i)
        if isinstance(methods,dict):
            newFunc.__doc__ = methods[i]
        setattr(NewAbstractClass,i,newFunc)
    NewAbstractClass._not_implemented = __not_implemented
    NewAbstractClass.mustInheritMethods = my_methods
    return NewAbstractClass
    
def call_abstract_constructors(classType, instance, method_handler = _default_method_handler):
    """
        The best way to use the AbstractClass is doing something like:
    
        class MyClass( AbstractClass(['method1','method2']) ):
            #whatever
        
        The problem is that as the type is dynamically generated, you can't call it from a
        constructor. Well, you can always do:
    
        AC = AbstractClass(['method1','method2'])
        
        class MyClass( AC ):
            def __init__(self):
                AC.__init__(self)
            #whatever
            
        But then the code looses its readibility. To avoid this problem, you can use this 
        function (call_abstract_constructors), providing the classType from where you are
        calling the function, the new instance, an, optionally, a method which will handle
        the unimplemented methods.
        
        It should be used as:
        
        class MyClass ( AbstractClass( ['method1','method2'] ) ):
            def __init__(self):
                call_abstract_constructors( MyClass, self )
            #whatever
            
        to ensure that you are calling the constructor.
        
        If for whatever the reason, you inherit from more than one AbstractClass, this 
        function will call the constructor of every AbstractClass. For example:
                
        class MyClass ( AbstractClass( ['method1','method2'] ), AbstractClass( ['method3','method4'] ) ):
            def __init__(self):
                call_abstract_constructors( MyClass, self) #Enogh for both AbstractClasses
    """
    for i in classType.__bases__:
        if __DEEPEST_CLASS in i.__bases__:
            i.__init__(instance,method_handler)


