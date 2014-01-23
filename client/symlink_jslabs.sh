#!/bin/bash

# This script symlinks the JSLABS directory to simplify development of JS-based experiment clients.
# If the JSLABS directory is symlinked developers no longer need to manually copy the files to the
# WAR directory for them to take effect.

ln -s ../../src/es/deusto/weblab/public/jslabs ./war/weblabclientlab/ 

