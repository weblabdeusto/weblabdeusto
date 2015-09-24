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
# Author: Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals
import thread as _thread
import threading as _threading
import new as _new
import types as _types
import sys as _sys
import datetime as _datetime
import voodoo.log as _log
import urllib2 as _urllib2
import __builtin__

"""
When trying to serialize something to XML or with pickle and so on, we
usually find that, since locks, files, and so on can't be serialized, the
module sometimes raises an exception.

In those cases, we can create a copy of the instance, acting as a Data Access
Object, with a deep copy of the information of the instance except fot these
types, and we will later serialize this instance.

This module just tries to avoid doing it with everytime.

Anyway, in some situations it might not work. It will happen when, trying to
serialize something that can't be serialized, an exception is raised. To
avoid this problem, just add the type of that class in the _default_exceptions,
or provide a sequence of exceptions as second parameter of dto_generator and
load_from_dto.

The other time when this module will fail is when you're handling some type
that we were not thinking on when writing this code (many types 0:-D). In that
case, you just have to add an "elif" in the get_dto_value.

In both cases, we would appreciate very much if you contact us to tell us how
to improve this module. Thank you in advance, and sorry for the inconveniences
0:-)
"""

try:
    file
    _file_base = file
except NameError:
    import io as _io
    _file_base = _io.IOBase

_default_exceptions = (
            _file_base,
            type,
            _new.classobj,
            _new.function,
            _new.instancemethod,
            _new.module,
            property,
            _types.BuiltinFunctionType,
            _types.BuiltinMethodType,
            _types.MethodType,
            _types.LambdaType
        )

_convert_to_str = (
            _urllib2.HTTPError,
        )

_basic_normal_types = (
            _datetime.datetime,
            _datetime.date,
            _datetime.time,
            bool,
            str,
            unicode,
            int,
            long,
            float,
            complex,
            _types.NoneType
        )

_recoverable_exceptions = (
            _thread.LockType,
            _threading._Condition
        )

class _DtoClass:
    pass

class _DtoObject(object):
    pass

class _DtoError(Exception):
    pass

class _DtoBuiltin(object):
    pass

class _DtoMissing(object):
    def __init__(self,name,element):
        self.name = name
        self.data_type = str(type(element))
        self.hash = hash(element)
    def __cmp__(self,other):
        if isinstance(other,_DtoMissing):
            if self.hash > other.hash:
                return 1
            elif self.hash < other.hash:
                return -1
            else:
                return 0
        else:
            return 1 # Always different

    def __eq__(self, other):
        return cmp(self, other) == 0

    def __ne__(self, other):
        return cmp(self, other) != 0

class _Node(object):

    BASIC     = 'basic'
    TUPLE     = 'tuple'
    LIST      = 'list'
    DICT      = 'dict'
    INSTANCE  = 'instance'
    OBJECT    = 'object'
    EXCEPTION = 'exception'
    BUILTIN_E = 'builtin_e'
    IGNORABLE = 'ignorable'

    def __init__(self,parent,name,element,address):
        self.parent    = parent
        self.name      = name
        self.element   = element
        self.children  = []
        self.address   = address
        self.data_type = self.get_data_type()
        self.repeated  = False

    def get_data_type(self):
        def is_builtin():
            if not hasattr(self.element, '__class__'):
                return False
            return self.element.__class__ == __builtin__.__dict__.get(self.element.__class__.__name__)

        if type(self.element) in _basic_normal_types:
            return _Node.BASIC
        elif type(self.element) == tuple:
            return _Node.TUPLE
        elif type(self.element) == list:
            return _Node.LIST
        elif type(self.element) == dict:
            return _Node.DICT
        elif is_builtin() or isinstance(self.element, _DtoBuiltin):
            return _Node.BUILTIN_E
        elif isinstance(self.element, Exception):
            return _Node.EXCEPTION
        elif type(self.element) == _new.instance:
            return _Node.INSTANCE
        elif hasattr(self.element,'__reduce__') or hasattr(self.element,'__reduce_ex__'):
            return _Node.OBJECT
        else:
            _log.log(_Node, _log.level.Warning, 'Unrecognized type: %s, %r, %r. Configure it at voodoo.mapper.py' % (type(self.element), self.name, self.parent))
            return _Node.IGNORABLE

    def _repr(self, n):
        parent = self.parent
        parents = str(self.name)
        while parent is not None:
            parents += " -> %s" % parent.name
            parent = parent.parent
        children = ""
        for child, childvalue in self.children:
            children += ' ' * n + "<child name='%s'>\n%s%s\n%s</child>\n" % (
                                        child,
                                        ' ' * (n + 1),
                                        childvalue._repr(n + 2),
                                        ' ' * n
                                    )
        if len(self.children) > 0:
            rc = "\n"
            jump = ' ' * (n - 1)
        else:
            rc = ""
            jump = ""
        return "<Node name='%s' parents='%s' type='%s' >%s%s%s</Node>" % (self.name, parents, self.data_type, rc, children, jump)

    def __repr__(self):
        return self._repr(1)

    def append_child(self,name,element):
        new_node = _Node(
                self, #parent
                name, #name
                element, #element
                self.address + (name,) #name
            )
        self.children.append((name, new_node))
        return new_node

class _InstanceDictionary(object):
    """
    A common dictionary is based on the hash of the keys. The
    problem is that some data types are not hasheable (for
    example dictionaries and lists), or eve tuples that have
    dictionaries or lists, for example. This is because, if
    they were hasheables, the hash could vary in time.

    Anyway, we can develop a dictionary which doesn't rely on
    the hash code of the keys, for situations where we know
    that the keys are not going to vary.
    """
    def __init__(self):
        # a list of tuples like (key,value)
        self.not_hasheable_instances = []
        self.hasheable_instances = {}

    def _is_hasheable(self,key):
        try:
            return not hasattr(key,'__getattr__') and hash(key) == hash(key)
        except:
            return False

    def has_key(self,key):
        if self._is_hasheable(key):
            return self.hasheable_instances.has_key(key)
        else:
            for i,j in self.not_hasheable_instances:
                try:
                    if i == key:
                        return True
                except TypeError:
                    return False
                except:
                    return False
            return False
    def keys(self):
        keys = self.hasheable_instances.keys()
        for i,j in self.not_hasheable_instances:
            keys.append(i)
        return keys

    def __getitem__(self,key):
        if self._is_hasheable(key):
            return self.hasheable_instances[key]
        else:
            for i,j in self.not_hasheable_instances:
                if i == key:
                    return j
            raise KeyError(key)

    def __setitem__(self,key,value):
        if self._is_hasheable(key):
            self.hasheable_instances[key] = value
        else:
            self.not_hasheable_instances.append((key,value))

    def __iter__(self):
        for i in self.hasheable_instances.keys():
            yield i
        for i,j in self.not_hasheable_instances:
            yield i

def remove_unpickables(instance):
    # This function tries to do the same as:
    # load_from_dto(dto_generator(obj), skip_recoverables = True )
    # in a far faster way


    already_removed_hash = {} # For those that can be hashed
    already_removed_nothash = {} # For those that can't be hashed:
                            # {
                            #    type(instance) : {
                            #           str(instance) : [instances]
                            #    }
                            # }

    def removing_unpickables(instance):
        type_instance = type(instance)

        if type_instance in _basic_normal_types:
            return instance

        if type_instance in _recoverable_exceptions:
            return None

        if issubclass(type_instance, _default_exceptions):
            return None

        if hasattr(instance, '__slots__') and not hasattr(instance, '__getstate__'):
            return None

        if type_instance in _convert_to_str:
            return str(instance)

        try:
            if already_removed_hash.has_key(instance):
                return instance
            else:
                was_hashable = True
                already_removed_hash[instance] = None
        except TypeError:
            was_hashable = False # Not hashable

        if not was_hashable:
            type_dict = already_removed_nothash.get(type_instance)
            str_instance = str(instance)
            if type_dict is None:
                already_removed_nothash[type_instance] = { str_instance : [instance] }
            else:
                inst_list = type_dict.get(str_instance)
                if inst_list is None:
                    type_dict[str_instance] = [instance]
                else:
                    for inst in inst_list:
                        try:
                            if instance == inst:
                                return instance
                        except:
                            pass

                    inst_list.append(instance)

        if type_instance == tuple:
            return tuple(( removing_unpickables(element) for element in instance ))
        elif type_instance == list:
            return [ removing_unpickables(element) for element in instance ]
        elif type_instance == dict:
            new_dict = {}
            for key, value in instance.iteritems():
                new_dict[removing_unpickables(key)] = removing_unpickables(value)
            return new_dict
        elif type_instance ==  _new.instance or hasattr(instance,'__reduce__') or hasattr(instance, '__reduce_ex__'):
            attributes = ( attr for attr in dir(instance)
                            #if not attr.startswith('__') or not attr.endswith('__')
                        )

            for attr in attributes:
                if hasattr(instance.__class__, attr):
                    data_type = getattr(instance.__class__, attr)
                    if type(data_type) == property:
                        continue
                    continue

                if isinstance(instance, Exception) and attr == 'message':
                    continue

                attr_value = getattr(instance, attr)
                setattr(instance, attr, removing_unpickables(attr_value))

            return instance
        else:
            return None

    result = removing_unpickables(instance)
    return result


def dto_generator(instance,exceptions = None):
    if exceptions == None:
        exceptions = _default_exceptions
    else:
        tmp_exceptions = ()
        for i in exceptions:
            tmp_exceptions = tmp_exceptions + (i,)
        exceptions = tmp_exceptions

    parsed_instances = _InstanceDictionary()

    def fill_tree(current_node,name,current_instance):
        """ fill_tree(current_node, name, current_instance)

        current_node     -> The current _Node.
        name             -> The name of current_instance
        current_instance -> The instance itself

        fill_tree will check if current_instance is not an exception
        and if it's not, it will add current_instance into current_node
        with name "name". After this, it will go through all information
        inside current_instance, and calling fill_tree with them.
        """
        for exce in exceptions:
            if issubclass(type(current_instance),exce):
                return

        if type(current_instance) in _recoverable_exceptions:
            # TODO: 2 references to the same missing instance
            # would create 2 different instances
            current_instance = _DtoMissing(name,current_instance)

        new_node = current_node.append_child(name,current_instance)
        if new_node.data_type in (_Node.BASIC, _Node.IGNORABLE):
            return # No information inside a basic data type

        # Don't repeat twice the same instance
        if parsed_instances.has_key(current_instance):
            parsed_instances[current_instance].append(new_node)
            for parsed_instance in parsed_instances[current_instance]:
                parsed_instance.repeated = True
            return
        else:
            parsed_instances[current_instance] = [new_node]
        if new_node.data_type in (_Node.TUPLE, _Node.LIST):

            # Tuples and lists have elements inside
            # They name will be their number
            for number,value in enumerate(current_instance):
                fill_tree(new_node,number,value)

        elif new_node.data_type == _Node.DICT:

            # Their name will be their key
            # Very important: in dictionaries, the values will be pairs of (key,value)
            for i in current_instance:
                fill_tree(new_node,i,(i,current_instance[i]))

        elif new_node.data_type in (_Node.INSTANCE, _Node.OBJECT, _Node.EXCEPTION, _Node.BUILTIN_E):
            # Elements are the elements which we will take
            elements = [ i for i in dir(current_instance)
                if not i.startswith('__') or not i.endswith('__')]

            for i in elements:
                if hasattr(current_instance.__class__,i):
                    data_type = getattr(current_instance.__class__,i)
                    if type(data_type) == property:
                        continue
                if isinstance(current_instance, Exception) and i == 'message':
                    continue # Deprecated
                element = getattr(current_instance,i)
                fill_tree(new_node,i,element)

        else:
            raise TypeError(
                'Unrecognized type: %s. Configure it at voodoo.mapper.py'
                % new_node.data_type
            )

    first_node = _Node(None,None,None,())
    fill_tree(first_node,None,instance)
    # At this point, instance_tree has been created
    dto_parsed_instances = _InstanceDictionary()

    # Let's create the dto structure
    def get_dto_value(current_node):
        if current_node.data_type == _Node.IGNORABLE:
            return "Unable to serialize this data type <%s>, so it was replaced by this str" % type(current_node)

        if current_node.data_type == _Node.BASIC:
            return current_node.element

        # Check parsed_instances
        if dto_parsed_instances.has_key(current_node.element):
            return dto_parsed_instances[current_node.element]

        if   current_node.data_type == _Node.TUPLE:

            new_tuple = ()
            for i,element in current_node.children:
                new_tuple = new_tuple + (get_dto_value(element),)
            dto_parsed_instances[current_node.element] = new_tuple
            return new_tuple

        elif current_node.data_type == _Node.LIST:

            new_list = []
            dto_parsed_instances[current_node.element] = new_list
            for i,element in current_node.children:
                new_list.append(get_dto_value(element))
            return new_list

        elif current_node.data_type == _Node.DICT:

            new_dict = {}
            dto_parsed_instances[current_node.element] = new_dict
            for i, element in current_node.children:
                # A dictionary is a set of tuples, where
                # the first element is the key and the
                # second element is the value
                this_tuple = get_dto_value(element)
                key   = this_tuple[0]
                value = this_tuple[1]
                new_dict[key] = value
            return new_dict

        elif current_node.data_type in (_Node.INSTANCE, _Node.OBJECT, _Node.EXCEPTION, _Node.BUILTIN_E):

            if current_node.data_type == _Node.EXCEPTION:
                new_instance = _DtoError()
            elif current_node.data_type == _Node.INSTANCE:
                new_instance = _DtoClass()
            elif current_node.data_type == _Node.BUILTIN_E:
                new_instance = _DtoBuiltin()
            else:
                new_instance = _DtoObject()

            dto_parsed_instances[current_node.element] = new_instance

            for i, element in current_node.children:
                setattr(new_instance,i,get_dto_value(element))

            new_instance._old_name      = current_node.element.__class__.__name__
            new_instance._old_doc       = current_node.element.__class__.__doc__
            new_instance._old_module    = current_node.element.__class__.__module__

            return new_instance

        else:
            raise TypeError(
                'Unrecognized type: %s. Configure it at voodoo.mapper.py, get_dto_value'
                % current_node.data_type
            )

    return get_dto_value(first_node.children[0][1])

def load_from_dto(instance,exceptions = None,skip_recoverables=False):
    if exceptions == None:
        exceptions = _default_exceptions
    else:
        tmp_exceptions = ()
        for i in exceptions:
            tmp_exceptions = tmp_exceptions + (i,)
        exceptions = tmp_exceptions

    parsed_instances = _InstanceDictionary()

    def fill_tree(current_node,name,current_instance):
        new_node = current_node.append_child(name,current_instance)

        if   new_node.data_type == _Node.BASIC or new_node.data_type == _Node.IGNORABLE:
            return # No information inside a basic data type

        # Don't repeat twice the same instance
        if parsed_instances.has_key(current_instance):
            parsed_instances[current_instance].append(new_node)
            for parsed_node in parsed_instances[current_instance]:
                parsed_node.repeated = True
            return
        else:
            parsed_instances[current_instance] = [new_node]

        if new_node.data_type in (_Node.TUPLE, _Node.LIST):

            # Tuples and lists have elements inside
            # They name will be their number
            for number,value in enumerate(current_instance):
                fill_tree(new_node,number,value)

        elif new_node.data_type == _Node.DICT:

            # Their name will be their key
            # Very important: in dictionaries, the values will be pairs of (key,value)
            for i in current_instance:
                fill_tree(new_node,i,(i,current_instance[i]))

        elif new_node.data_type in (_Node.INSTANCE, _Node.OBJECT, _Node.EXCEPTION, _Node.BUILTIN_E):

            # Elements are the elements which we will take
            elements = [ i for i in dir(current_instance)
                if not i.startswith('__') or not i.endswith('__')]

            for i in elements:
                if new_node.data_type == _Node.EXCEPTION and i == 'message':
                    continue # Deprecated
                element = getattr(current_instance,i)
                fill_tree(new_node,i,element)

        else:
            raise TypeError(
                'Unrecognized type: %s. Configure it at voodoo.mapper.py'
                % new_node.data_type
            )

    first_node = _Node(None,None,None,())
    fill_tree(first_node,None,instance)
    # At this point, instance_tree has been created

    dto_parsed_instances = _InstanceDictionary()

    # Let's create the dto structure
    def load_dto_value(current_node):
        if current_node.data_type == _Node.BASIC:
            return current_node.element

        # Check parsed_instances
        if dto_parsed_instances.has_key(current_node.element):
            return dto_parsed_instances[current_node.element]

        if   current_node.data_type == _Node.TUPLE:

            new_tuple = ()
            for i,element in current_node.children:
                new_tuple = new_tuple + (load_dto_value(element),)
            dto_parsed_instances[current_node.element] = new_tuple
            return new_tuple

        elif current_node.data_type == _Node.LIST:

            new_list = []
            dto_parsed_instances[current_node.element] = new_list
            for i, element in current_node.children:
                new_list.append(load_dto_value(element))
            return new_list

        elif current_node.data_type == _Node.DICT:

            new_dict = {}
            dto_parsed_instances[current_node.element] = new_dict
            for i, element in current_node.children:
                # A dictionary is a set of tuples, where
                # the first element is the key and the
                # second element is the value
                this_tuple = load_dto_value(element)
                key   = this_tuple[0]
                value = this_tuple[1]
                new_dict[key] = value
            return new_dict

        elif current_node.data_type == _Node.BUILTIN_E:
            dto_object = _DtoBuiltin()

            for i, element in current_node.children:
                setattr(dto_object,i,load_dto_value(element))

            builtin_type = getattr(__builtin__, dto_object._old_name)
            inst = builtin_type()

            for i, element in current_node.children:
                try:
                    setattr(inst,i,load_dto_value(element))
                except AttributeError:
                    pass

            dto_parsed_instances[current_node.element] = inst
            try:
                del inst._old_module
                del inst._old_name
            except AttributeError:
                pass
            return inst

        elif current_node.data_type in (_Node.INSTANCE, _Node.OBJECT, _Node.EXCEPTION):
            if current_node.data_type == _Node.INSTANCE:
                dto_object = _DtoClass()
            elif current_node.data_type == _Node.OBJECT:
                dto_object = _DtoObject()
            else:
                dto_object = _DtoError()

            dto_parsed_instances[current_node.element] = dto_object

            for i, element in current_node.children:
                setattr(dto_object,i,load_dto_value(element))

            old_module = dto_object._old_module
            old_name = dto_object._old_name
            __import__(old_module,globals(),locals(),[])
            the_class = getattr(_sys.modules[old_module],old_name)
            dto_object.__class__ = the_class

            if hasattr(dto_object,'deserialize'):
                dto_object.deserialize()

            del dto_object._old_module
            del dto_object._old_name

            if isinstance(dto_object,_DtoMissing):
                if skip_recoverables:
                    return None
                # it is a DtoMissing
                if dto_object.data_type == str(_thread.LockType):
                    l = _threading.Lock()
                    dto_parsed_instances[current_node.element] = l
                    return l
                elif dto_object.data_type == str(_threading._Condition):
                    c = _threading.Condition()
                    dto_parsed_instances[current_node.element] = c
                    return c
                else:
                    raise TypeError(
                        """No handler for the missing value %s at %s.
                    Check that you don't have a value in _recoverable_exceptions,
                    and no handler in load_from_dto"""
                            % (i,dto_object)
                        )
            return dto_object
        else:
            raise TypeError(
                'Unrecognized type: %s. Configure it at voodoo.mapper.py, load_dto_value'
                % current_node.data_type
            )

    return load_dto_value(first_node.children[0][1])

