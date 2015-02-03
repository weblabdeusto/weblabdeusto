#!/bin/sh
### BEGIN INIT INFO
# Provides:		romie_server
# Required-Start:	$network $syslog
# Required-Stop:	$network $syslog
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	Romie server daemon
# Description:
#
### END INIT INFO

case "$1" in
  start)
    echo "Starting RoMIE Server"
    /usr/bin/romie-server.py&
    ;;
  stop)
    echo "Stopping RoMIE server"
    killall romie-server.py
    ;;
  *)
    echo "Usage: service romie_server {start|stop}"
    exit 1
    ;;
esac


exit 0
