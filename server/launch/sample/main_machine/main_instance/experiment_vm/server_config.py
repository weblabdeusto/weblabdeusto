#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

# This variable contains a path, which should point to the place 
# where the Virtual Machine images are stored. In the case of Virtual 
# Box, this will be the "Machines" folder, which under Windows is 
# often located under "c:/Users/<user_name>/.VirtualBox". Its exact 
# location might nonetheless vary depending on the Operating System 
# used, the Virtual Machine system and the local configuration.
vm_storage_dir = """C:\\Users\\lrg\\.VirtualBox\\Machines"""

# Variables prefixed with "vbox" are specific to the Virtual Box 
# Virtual Machine software. 

# Name of the Virtual Box machine which this experiment uses. 
# Should contain the name of the machine, which will often be
# different than the Hard Disk name.
vbox_vm_name = "UbuntuDefVM2"

# Name of the snapshot to which the Virtual Machine will be 
# restored before every experiment use. The specified snapshot
# should feature a functional machine, already started and with
# the experiment ready to use. That way, the user will be able to
# start experimenting with it as fast as possible. 
# It is particularly important to make sure that the snapshot is
# taken of an already started machine ( at the desktop, and with the
# password changing and remote desktop software running ).
vbox_base_snapshot = "Ready"

# The URL of the Virtual Machine. This is the URL that will be provided 
# to the users for them to connect to, through their remote desktop
# software of choice. (Currently, either RDP or VNC).
vm_url = "vnc://192.168.51.82:5901"

# The Virtual Machine software to use. Currently, only VirtualBox
# is supported, though the sytem is designed to be easily extensible
# and it shouldn't be particularly hard to add support for another
# one. (A new class with the appropriate name would need to be
# implemented, supporting the same interface).
vm_vm_type = "VirtualBox"

# The User Manager to employ. The User Manager prepares the machine
# for use, sending the appropriate query to it to change the password
# of the Virtual Machine. The default one, HttpQueryUserManager, is
# compatible with the VNC and RDP password changers that WebLab
# provides, and will simply send the request through HTTP to the
# URL specified below. Though the system is designed to be extensible,
# generally it won't be advisable to create a custom User Manager.
# In fact, even if we were to use a custom protocol with a custom
# password changer, it would be relatively easy to simply have it
# listen for this particular http query.
vm_user_manager_type = "HttpQueryUserManager"

# This is the URL to which password changing queries done by the
# default UserManager, HttpQueryUserManager, will be sent. This is,
# hence, the URL on which the password changing services should 
# listen. It is important to make sure that the specified port
# here and the specified port in the password changing service
# configuration do match. 
# When deploying an experiment for real use, it is important to configure
# the firewall correctly. The password of the Virtual Machine can be changed
# with a simple HTTP query to the right port. There is no authentication 
# system. Hence, only the WebLab VM experiment server should be allowed
# to contact the Virtual Machine through this port.
http_query_user_manager_url = "http://192.168.51.82:18080"

# Will save the image after every use if enabled. Generally, this is
# not advisable. In the future, support for snapshot saving might be
# implemented.
vm_should_store_image = False

# Should specify the estimated load time of the Virtual Machine. This time
# will be displayed to the users, so that they know the waiting time they
# should expect.
vm_estimated_load_time = 20


# It is possible to add certain optional arguments for starting up the Virtual Machines. 
# These won't generally be needed, and hence the line below is commented out by default.
# vbox_headless_start_options = ['-vrde', 'on']
