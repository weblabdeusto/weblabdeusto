#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

import sys
import os.path
import re

if len(sys.argv) != 2:
    print >>sys.stderr, "%s: parameter missing" % sys.argv[0]
    print >>sys.stderr, "Usage: %s LOG_FILE" % sys.argv[0]
    sys.exit(-1)

if not os.path.exists(sys.argv[1]):
    print >>sys.stderr, "%s: invalid parameter" % sys.argv[0]
    print >>sys.stderr, "Usage: %s LOG_FILE" % sys.argv[0]
    sys.exit(-2)

started = {
    # 
    # The keys might be repeated, but the collision will be very low.
    # 
    # Since they might be repeated, we will show all the lines of log (both of 
    # starting and ending) with a key that has at least one not finished entry.
    # 
    # 'call_id' : (number, [line_start1, line_start2], [line_end1, line_end2])
    #
}

CALL_ID_REGEX = '([0-9]{4}_[0-9]{2}_[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2}-[a-zA-Z0-9]{12})'
CALL_START_REGEX = r'.*\+{4}%s\+{4}.*'
CALL_END_REGEX   = r'.*\-{4}%s\-{4}.*'

for line in open(sys.argv[1]):
    mo = re.match(CALL_START_REGEX % CALL_ID_REGEX, line)
    if mo != None:
        call_id = mo.groups()[0]
        if started.has_key(call_id):
            number, lines_start, lines_end = started[call_id]
            lines_start.append(line)
            started[call_id][0] = number + 1
        else:
            started[call_id] = [1, [line], []]

    else:
        mo = re.match(CALL_END_REGEX % CALL_ID_REGEX, line)
        if mo != None:
            call_id = mo.groups()[0]
            if started.has_key(call_id):
                number, lines_start, lines_end = started[call_id]
                if number == 1:
                    started.pop(call_id)
                else:
                    lines_end.append(line)
                    started[call_id][0] = number - 1

for call_id in started:
    print started[call_id][1:]

