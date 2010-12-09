#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

vm_storage_dir = """C:\Users\lrg\.VirtualBox\Machines"""

vbox_vm_name = "UbuntuVM"

#vm_url = "vnc://192.168.51.119:5900"
vm_url = "vnc://192.168.51.81:5900"
vm_vm_type = "VirtualBox"
vm_user_manager_type = "HttpQueryUserManager"
vm_should_store_image = False
vm_prepare_name = {"""C:\Users\lrg\.VirtualBox\HardDisks\UbuntuVM.vdi""" : """C:\Users\lrg\VBoxOrig\HardDisks\UbuntuVM.vdi"""}

http_query_user_manager_url = "http://192.168.51.81:18080"