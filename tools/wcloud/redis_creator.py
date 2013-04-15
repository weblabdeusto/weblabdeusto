import shutil
import os
import sys
import traceback

from optparse import OptionParser


if __name__ == '__main__':
    #Set options
    parser = OptionParser(usage =  "Redis creator creates a set of idle redis instances to be used by the WebLab-Deusto instances."
                                                   "They will be called redis.0.conf - redis.63.conf.\n\n"
                                                   "Example:\n\n"
                                                   "   python redis_creator.py -p 6380 -s 0 -e 63 -t redis_template\n\n"
                                                   "Will assume that you have downloaded and compiled redis into a directory called 'redis_template'"
                                                   "and the ports used will be from 6380 to 6443 in 63 copies (16 x 63 >= 1000).")

    parser.add_option('-p', '--port', dest='port', metavar="INITIAL_PORT",
                        help="initial port",
                        type="int", default=6380)
    
    parser.add_option('-s', '--start', dest='start', metavar="START_POINT",
                        help="Start point for instances used",
                        type="int",
                        default=0)
    
    parser.add_option('-e', '--end', dest="end", metavar="END_POINT",
                        help="End point for instances required",
                        type="int")

    parser.add_option('-t', '--template', dest='template', metavar="TEMPLATE_DIR",
                        help="Redis template directory", default="redis_template",
                        type="str")

    args, _ = parser.parse_args()

    if not os.path.exists(args.template):
        print >> sys.stderr, "Directory template %s not found" % args.template
        sys.exit(-1)

    if not os.path.exists(os.path.join(args.template, 'redis.conf')):
        print >> sys.stderr, "redis.conf file not found in %s" % args.template
        sys.exit(-2)

    REDIS_CONF = open(os.path.join(args.template, 'redis.conf')).read()

    if not os.path.exists(os.path.join(args.template, 'var')):
        print >> sys.stderr, "var directory not found in %s" % args.template
        sys.exit(-2)

    current_port = args.port

    for n in range(args.start, args.end):
        print "Creating %s..." % n,
        try:
            shutil.copytree(os.path.join(args.template, 'var'), os.path.join(args.template, 'var%s' % n))
            current_config = REDIS_CONF.replace('/var/','/var%s/' % n)
            lines = current_config.splitlines()
            pos = [ pos for pos, line in enumerate(lines) if line.startswith("port ") ][0]
            lines[pos] = 'port %s' % current_port
            current_config = '\n'.join(lines)
            open(os.path.join(args.template, 'redis.%s.conf' % n), 'w').write(current_config)
            current_port += 1
        except:
            print "[error]"
            traceback.print_exc()
        else:
            print "[done]"
