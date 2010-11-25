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

if __name__ != '__main__':
    raise RuntimeError("module %s should never be imported, it's just an examples file" % __name__)

import voodoo.abstraction.abstract_class_generator as acg

#################################################################################
#                                                                               #
#       These are examples in Python using abstract_class_generator and         #
#       their aproximated equivalent in a variant of C# (chosen as an           #
#       example of staticly typed object oriented language) which would         #
#       support multiple inheritance.                                           #
#                                                                               #
#################################################################################



#################################################################################
#                                                                               #
#       abstract class A{                                                       #
#               void methodA(){                                                 #
#                       Console.WriteLine("hello, I'm A");                      #
#               }                                                               #
#       }                                                                       #
#                                                                               #
#################################################################################

class A(acg.AbstractClass()):
    """ Primary abstract class: it inherits from AbstractClass """
    def __init__(self):
        #In order to call the constuctor of the parent AbstractClass
        #class, we use this method of the module
        acg.call_abstract_constructors(A,self)
        #As there is no more code in A's constructor, and A doesn't 
        #inherit from more classes, we don't really need to implement 
        #this constructor
        
    def methodA(self):
        print "hello, I'm A"

#################################################################################
#                                       #
#   class B{                                #
#       void methodB(){                         #
#           Console.WriteLine("hello, I'm B");          #
#       }                               #
#       }                                                                       #
#                                       #
#################################################################################

class B:
    def methodB(self):
        print "hello, I'm B"

#################################################################################
#                                       #
#   abstract class C : A , B {                                              #
#                                                                               #
#                abstract void methodCb();                                      #
#                                                                               #
#                void methodC(){                                                #
#                       Console.WriteLine("hello, I'm C");                      #
#                }                                                              #
#       }                                                                       #
#                                                                               #
#################################################################################

class C(B,A,acg.AbstractClass(['methodCb'])):
    """ Primary abstract class: it inherits from AbstractClass """
    def __init__(self):
        #We must call all constructors
        #B constructor (no constructor implemented in B):
        #B.__init__(self)
        #A constructor (needed)
        A.__init__(self)
        #Dinamically generated AbstractClass class
        acg.call_abstract_constructors(C,self)
    def methodC(self):
        print "hello, I'm C"

#################################################################################
#                                                                               #
#       class D {                                                               #
#               void methodD(){                                                 #
#                       Console.WriteLine("hello, I'm D");                      #
#               }                                                               #
#       }                                                                       #
#                                                                               #
#################################################################################

class D:
    def methodD(self):
        print "hello, I'm D"

#################################################################################
#                                                                               #
#       /* It's abstract as it doesn't implement the abstract method            #
#       *  methodCb inherited from C                                            #
#       */                                                                      #
#       abstract class E : C , D {                                              #
#               void methodE(){                                                 #
#                       Console.WriteLine("hello, I'm E");                      #
#               }                                                               #
#       }                                                                       #
#                                                                               #
#################################################################################

class E(C,D):
    """ 
        Laboratory abstract class: doesnt inherit directly from
        AbstractClass, but inherits unimplemented methods that
        doesn't implement, like methodCb
    """
    def methodE(self):
        print "hello, i'm E"

#################################################################################
#                                                                               #
#       /* It's not abstract as it does implement all unimplemented methods     #
#       */                                                                      #
#       class F : E {                                                           #
#               override void methodCb(){                                       #
#                       Console.WriteLine("hello, I'm Cb in F");                #
#               }                                                               #
#                                                                               #
#               void methodF(){                                                 #
#                       Console.WriteLine("hello, I'm F");                      #
#               }                                                               #
#       }                                                                       #
#                                                                               #
#################################################################################


class F(E):
    """ Normal class, as it doesn't have any unimplemented method """
    def methodCb(self):
        print "hello, I'm Cb in F"
    def methodF(self):
        print "hello, I'm F"

#################################################################################
#                                                                               #
#       /* A is abstract, but doesn't have any abstract method, so G is not     #
#       *  abstract                                                             #
#       */                                                                      #
#       class G : A {                                                           #
#       }                                                                       #
#                                                                               #
#################################################################################

class G(A):
    """ Normal class, as it doesn't have any unimplemented method """
    pass


#################################################################################
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  #
#################################################################################


#################################################################################
#                                                                               #
#              CHECKING THE BEHAVIOUR OF THESE CLASSES                          #
#                                                                               #
#################################################################################

def instanciate(what):
    print "Instanciating %s...\t\t\t" % what.__name__ ,
    try:
        what()
    except Exception, e:
        print e,'\t',e.__class__
    else:
        print "done"

CHAR_NUMBER=130
print
print
print '*'*CHAR_NUMBER
print "Instanciating classes A - G: "
print 
instanciate(A)
instanciate(B)
instanciate(C)
instanciate(D)
instanciate(E)
instanciate(F)
instanciate(G)
print '*'*CHAR_NUMBER
print
print

#################################################################################
#                                                                               #
#                 CHANGING DEFAULT BEHAVIOURS                                   #
#                                                                               #
#################################################################################

class H(acg.AbstractClass(['methodH'])):
    """ 
        H is just another primary abstract class, but we want to change the
        behaviour whenever someone instance a class which inherits from H,
        printing a message instead of raising an exception.
        We will use the function "H_handler"
    """
    def __init__(self):
        acg.call_abstract_constructors(H,self,H_handler)

class I(H):
    pass

def H_handler(methods):
    print "Error! %s not implemented!\t\t\t" % methods,

def J_handler(instance):
    print "Trying to instanciate abstract class '%s'!\t\t" % instance.__class__.__name__,

class J(acg.AbstractClass()):
    _abstract_handler = J_handler

print '*'*CHAR_NUMBER
print "Instanciating I and J"
print

print "Instanciating I...\t\t\t",
i = I()
print "done"

print "Calling methodH of I instance...\t",
try:
    i.methodH()
except Exception, e:
    print e,'\t\t\t\t\t\t',e.__class__
instanciate(J)
print '*'*CHAR_NUMBER
print
print

#################################################################################
#                                                                               #
#                ADDING MORE INFORMATION TO CLASSES                             #
#                                                                               #
#################################################################################

class K(acg.AbstractClass()):
    pass

class L(acg.AbstractClass([],'BaseClassName')):
    pass

class M(acg.AbstractClass(
            {
                'methodM'   :   'Documentation for methodM',
                'methodM2'  :   'Documentation for methodM2'
            }
        )
    ):
    pass

print '*'*CHAR_NUMBER
print 'Getting the parent classes from K and L'
print 

print 'Parent class of K...\t\t',K.__bases__,'\t',K.__bases__[0].__name__
print 'Parent class of L...\t\t',L.__bases__,'\t',L.__bases__[0].__name__
print '*'*CHAR_NUMBER
print 
print

print '*'*CHAR_NUMBER
print 'Getting documentation from methods from M'
print 
print 'Method methodM:\t\t\t\t',M.methodM.__doc__
print 'Method methodM2:\t\t\t',M.methodM2.__doc__
print '*'*CHAR_NUMBER
print
print

#################################################################################
#                                                                               #
#                DOCUMENTING ABSTRACT METHODS                                   #
#                                                                               #
#################################################################################

class N(acg.AbstractClass(['methodN','methodNb'])):
    def methodN(self):
        """
            This is just another way to write the abstract method.
            As long as 'methodN' is declared in the AbstractClass,
            this method will be considered abstract, so the rest
            of the code will have the same behaviour as if this
            method was not implemented here.

            Anyway, if we are going to enable inherited classes to
            be instanciated even if they don't implement this method,
            we should write here "self._not_implemented(methodname)",
            so if someone calls the unimplemented method, a
            NotImplementedError is raised.

            To sum up, this method is just a way to document and show
            the abstract methods in a more familiar way.
        """
        self._not_implemented('methodN')
    def methodNb(self):
        """documentation for methodNb"""
        self._not_implemented('methodNb')
    
    #We allow the subclasses to be instanciated without implementing methodN and methodNb
    def __init__(self): 
        acg.call_abstract_constructors(N,self,lambda _ : None)

class O(N):
    pass

print '*'*CHAR_NUMBER
print 'Instanciating O...\t\t\t',
o = O()
print 'done'
print 'Showing documentation of methodNb...\t',
print o.methodNb.__doc__
print 'Calling methodNb...\t\t\t',
try:
    o.methodNb()
except Exception, e:
    print e,'\t\t\t\t\t\t',e.__class__
print '*'*CHAR_NUMBER
print
print 
