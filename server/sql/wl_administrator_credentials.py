#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

# XXX WARNING: 
# This file contains the username and password of the WebLab administrator in MySQL
# The system will never use this username, its purpose is to be used by the administrator
# of the WebLab with MySQL client when administration tasks are needed.

# This user is created through:
# mysql -uroot -p < create_wl_administrator.sql

# This user can modify things in the whole MySQL system, so this file shouldn't be able to
# be read by other users (chmod 600 wl_administrator_credentials.py)

ADMINISTRATOR_USER="wl_administrator"
ADMINISTRATOR_PASSWORD="wl_administrator_password"

