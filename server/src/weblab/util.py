from __future__ import print_function, unicode_literals
import os
import sys

def data_filename(fname):
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if os.path.exists(os.path.join(basedir, 'weblabdeusto_data', fname)):
        return os.path.join(basedir, 'weblabdeusto_data', fname)
    if os.path.exists(os.path.join(sys.prefix, 'weblabdeusto_data', fname)):
        return os.path.join(sys.prefix, 'weblabdeusto_data', fname)
    elif os.path.exists(os.path.join(basedir, fname)):
        return os.path.abspath(os.path.join(basedir, fname))
    elif os.path.exists(os.path.join(basedir, '..', '..', 'client', fname)):
        return os.path.abspath(os.path.join(basedir, '..', '..', 'client', fname))
    else:
        return fname
