#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

import sys
import traceback

try:
    import numpy as np
except ImportError:
    NUMPY_AVAILABLE = False
else:
    NUMPY_AVAILABLE = True

PRINT_FULL_TRACE = False

class BotError(object):

    def __init__(self, (exception, trace), max_number=0, min_number=0, avg_number=0):
        super(BotError, self).__init__()
        self.instances = [(exception, trace)]
        self.max = max_number
        self.min = min_number
        self.avg = avg_number

    def get_name(self):
        return self.instances[0].__class__.__name__

    def add_instance(self, (exception, trace)):
        self.instances.append((exception, trace))

    def set_max(self, number):
        self.max = number

    def set_min(self, number):
        self.min = number

    def set_avg(self, number):
        self.avg = number

    def __repr__(self):
        s = "<BotError max='%s' min='%s' avg='%s'><instances>" % (self.max, self.min, self.avg)
        for instance, trace in self.instances:
            s += '<Exception type="%s" str="%s">%s</Exception>' % (instance.__class__.__name__, str(instance), trace)
        return s + "</instances></BotInstance>"

class BotIteration(object):

    def __init__(self, time, exceptions, botusers, out, err):
        super(BotIteration, self).__init__()
        self.time = time
        self.exceptions = exceptions
        self.botusers   = botusers
        self.out        = out
        self.err        = err

    def dispose(self):
        data = []
        for botuser in self.botusers:
            user_data = []
            for call in botuser.bot.calls:
                user_data.append( (call.begin, call.end, call.method) )
            data.append(user_data)
            botuser.dispose()

        if PRINT_FULL_TRACE:
            print(repr(data))

    def get_times(self):
        return [ botuser.time() for botuser in self.botusers ]

    def get_routes(self):
        return [ botuser.route for botuser in self.botusers ]

    def get_number_of_exceptions(self):
        number_of_exceptions = 0
        for botuser in self.botusers:
            number_of_exceptions += botuser.get_number_of_exceptions()
        return number_of_exceptions

    def get_exceptions(self):
        exceptions_lists = [ self.exceptions[exception_name].instances for exception_name in self.exceptions ]
        exceptions = []
        for exceptions_list in exceptions_lists:
            exceptions.extend(exceptions_list)
        return exceptions

    def _get_xxx_time_per_call_by_name(self, func):
        xxx_by_name = {}

        all_calls_by_name = self.get_all_calls_by_name()

        for call_name in all_calls_by_name:
            xxx_by_name[call_name] = func([
                                call.time()
                                for call in all_calls_by_name[call_name]
                            ]
                    )
        return xxx_by_name

    def get_all_calls_by_name(self):
        users_calls_by_name = [ botuser.get_calls_by_name().keys() for botuser in self.botusers ]
        calls_by_name = []
        for user_call_by_name in users_calls_by_name:
            for call_by_name in user_call_by_name:
                if not call_by_name in calls_by_name:
                    calls_by_name.append(call_by_name)

        all_calls_by_name = {}
        for call_name in calls_by_name:
            all_calls = []
            for botuser in self.botusers:
                all_calls.extend(botuser.get_calls_by_name().get(call_name) or [])
            all_calls_by_name[call_name] = all_calls
        return all_calls_by_name

    def get_max_time_per_call_by_name(self):
        return self._get_xxx_time_per_call_by_name(max)

    def get_min_time_per_call_by_name(self):
        return self._get_xxx_time_per_call_by_name(min)

    def get_avg_time_per_call_by_name(self):
        return self._get_xxx_time_per_call_by_name(np.mean)

    def get_std_time_per_call_by_name(self):
        return self._get_xxx_time_per_call_by_name(np.std)

    def get_number_of_exception_instances(self, exception_name):
        if exception_name in self.exceptions:
            return len(self.exceptions[exception_name].instances)
        else:
            return 0

    def __repr__(self):
        s = "<BotIteration: time='%s'><exceptions>" % self.time
        for exc in self.exceptions:
            s += repr(exc)
        s += '</exceptions><botusers>'
        for botuser in self.botusers:
            s += repr(botuser)
        s += '</botusers><out>'
        s += self.out
        s += '</out><err>'
        s += self.err
        return s + '</err></BotIteration>'

class BotTrial(object):

    def __init__(self, iterations):
        super(BotTrial, self).__init__()
        self.iterations = iterations
        self.compile()

    def compile(self):
        times = []
        number_of_exceptions = []
        exceptions = {}
        for iteration in self.iterations:
            times.extend(iteration.get_times())
            number_of_exceptions.append(iteration.get_number_of_exceptions())
            self._add_exceptions(exceptions, iteration.get_exceptions())

        for exception_name in exceptions:
            number_of_exception_instances = []
            for iteration in self.iterations:
                number_of_exception_instances.append(iteration.get_number_of_exception_instances(exceptions[exception_name].get_name()))
            exceptions[exception_name].set_max(max(number_of_exception_instances))
            exceptions[exception_name].set_min(min(number_of_exception_instances))
            exceptions[exception_name].set_avg(np.mean(number_of_exception_instances))

        self.max_time = max(times)
        self.min_time = min(times)
        self.avg_time = np.mean(times)
        self.std_time = np.std(times)
        self.max_exceptions = max(number_of_exceptions)
        self.min_exceptions = min(number_of_exceptions)
        self.avg_exceptions = np.mean(number_of_exceptions)
        self.exceptions = exceptions

        method_names = self.get_method_names()

        self.max_call_times = {}
        self.min_call_times = {}
        for method_name in method_names:
            self.max_call_times[method_name] = max([ (it.get_max_time_per_call_by_name().get(method_name) or 0) for it in self.iterations ])
            self.min_call_times[method_name] = min([ (it.get_min_time_per_call_by_name().get(method_name) or 365 * 24 * 3600) for it in self.iterations ])


        all_calls = {}
        for iteration in self.iterations:
            all_calls_by_name = iteration.get_all_calls_by_name()
            for method_name in all_calls_by_name:
                if method_name in all_calls:
                    all_calls[method_name].extend(all_calls_by_name[method_name])
                else:
                    all_calls[method_name] = all_calls_by_name[method_name][:]

        self.avg_call_times = {}
        self.std_call_times = {}
        for method_name in method_names:
            self.avg_call_times[method_name] = np.mean( [ call.time() for call in all_calls[method_name] ])
            self.std_call_times[method_name] = np.std( [ call.time() for call in all_calls[method_name] ])

        # All data calculated, cleaning...
        for iteration in self.iterations:
            iteration.dispose()

    def get_method_names(self):
        method_names = []
        for iteration in self.iterations:
            for call_name in iteration.get_max_time_per_call_by_name():
                if not call_name in method_names:
                    method_names.append(call_name)
        return method_names


    def _add_exception(self, exceptions_dict, exception):
        """ { "ExceptionType1": <BotError>, "ExceptionType2": <BotError>, ... } """
        if exception.__class__.__name__ in exceptions_dict:
            exceptions_dict[exception.__class__.__name__].add_instance(exception)
        else:
            exceptions_dict[exception.__class__.__name__] = BotError(exception)

    def _add_exceptions(self, exceptions_dict, exceptions):
        for exception in exceptions:
            self._add_exception(exceptions_dict, exception)

    def __repr__(self):
        s = "<BotTrial max_time='%s' min_time='%s' avg_time='%s' std_time='%s' max_exceptions='%s' min_exceptions='%s' avg_exceptions='%s'><exceptions>" % (self.max_time, self.min_time, self.avg_time, self.std_time, self.max_exceptions, self.min_exceptions, self.avg_exceptions)
        for exc in self.exceptions:
            s += repr(exc)
        s += '</exceptions><iterations>'
        for iteration in self.iterations:
            s += repr(iteration)
        return s + "</iterations></BotTrial>"

    def print_results(self, fobj = sys.stdout):
        result = self.botlauncher.get_results()
        print("", file=fobj)
        print("  max user time:", result.max_time, file=fobj)
        print("  avg user time:", result.avg_time, file=fobj)
        print("  min user time:", result.min_time, file=fobj)
        print("", file=fobj)
        print("  max iteration exceptions:", result.max_exceptions, file=fobj)
        print("  avg iteration exceptions:", result.avg_exceptions, file=fobj)
        print("  min iteration exceptions:", result.min_exceptions, file=fobj)
        print("", file=fobj)
        print("  max call time: ", result.max_call_times, file=fobj)
        print("  avg call time: ", result.avg_call_times, file=fobj)
        print("  min call time: ", result.min_call_times, file=fobj)
        print("", file=fobj)
        for exception_name in result.exceptions:
            print("", file=fobj)
            print("  For exception...", exception_name, file=fobj)
            print("    max times:", result.exceptions[exception_name].max, file=fobj)
            print("    avg times:", result.exceptions[exception_name].avg, file=fobj)
            print("    min times:", result.exceptions[exception_name].min, file=fobj)
            print("    instances:", result.exceptions[exception_name].instances, file=fobj)
        print("", file=fobj)
        print("  Let's go for each iteration...", file=fobj)
        for iteration in result.iterations:
            print("", file=fobj)
            print("    iteration", file=fobj)
            print("      time:", iteration.time, file=fobj)
            for exception_name in iteration.exceptions:
                print("      exception: %s (%i)" % (exception_name, len(iteration.exceptions[exception_name].instances)), iteration.exceptions[exception_name].instances, file=fobj)
                for e in iteration.exceptions:
                    print(traceback.format_exc(e), file=fobj)
            print("    out: ", iteration.out, file=fobj)
            print("    err: ", iteration.err, file=fobj)
        fobj.flush()

