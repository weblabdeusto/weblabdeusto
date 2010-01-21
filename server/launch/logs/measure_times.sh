#!/bin/bash
#
# It returns how long did a method take, given the logs:
# 
# Example:
# for i in do_get_networks do_get_server do_new_query; do grep $i sample__voodoo_gen_coordinator_logs.txt|./measure_times.sh > resultados_$i; done
# 
# TODO: Why can't I do that as a pipe?
# 
grep "started at"|awk '{ print $13 " " $2 " " $9 }'|sed -e 's/>//' > results.tmp.file

python << EOF
import time
for s in open('results.tmp.file'):
	date1, date2 = s.split(' ')[:2]
	milli1 = float("0." + date1.split(',')[1])
	milli2 = float("0." + date2.split(',')[1])
	time_struct1 = time.strptime("2009:" + date1.split(',')[0],"%Y:%H:%M:%S")
	time_struct2 = time.strptime("2009:" + date2.split(',')[0],"%Y:%H:%M:%S")
	total1 = time.mktime(time_struct1) + milli1
	total2 = time.mktime(time_struct2) + milli2
	print total2 - total1, ' '.join(s.split(' ')[2:])[:-1]
EOF
