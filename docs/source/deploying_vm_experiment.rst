.. _toctree-directive:
.. _deploying_vm_experiment:

Introduction
============

WebLab-Deusto supports two kinds of experiments: **Managed** and **Unmanaged** experiments.

Managed experiments are fully integrated with WebLab-Deusto and, generally, 
developed specifically for it through the use of its provided API. Data during the 
experiment tends to be transmitted through WebLab, which means logging and accountability 
is both easy and accurate. They are the most frequent kind of experiment, and, 
when possible, it is the most advisable type of experiment to use. 
However, it is not always possible or convenient to have such integration. 
Sometimes, an experiment developer might be unable or unwilling to adequate 
his experiment, due to the nature of the experiment itself or the time it would require to 
do so. For these cases, WebLab-Deusto provides Virtual Machine based Unmanaged experiments.


.. image:: /_static/weblab_vm.png
   :width: 300 px
   :align: center


Virtual Machine Experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~

Virtual Machine experiments work differently than traditional Managed experiments. A Virtual Machine experiment does not include any WebLab-specific code. 
Instead, the experiment is developed anyhow and deployed on a Virtual Machine image. WebLab-Deusto then manages that Virtual Machine. 
WebLab-Deusto users will, upon experiment startup through the standard WebLab-Deusto web, receive a password. Then, they may use that password to connect to the 
Virtual Machine through either Remote Desktop or VNC. From then on, the user can freely use the Virtual Machine and the experiment deployed on it. 
Once the time has run out, WebLab-Deusto will close the Virtual Machine and restore it to a pre-defined snapshot before the next use.


Supported Virtual Machine, OSes, and Protocols
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently WebLab-Deusto VM system has been tested on Linux, under which the VNC protocol through the TightVNC server (and compatible clients) is supported. 
It has also been tested on Windows, under which both UltraVNC and Remote Desktop are supported.

The Virtual Machine software currently supported is Virtual Box.

It is noteworthy that this list is likely to be extended in the future, and that the system is easily extensible, so it would not be particularly hard for a developer to add support to new 
VM software or new Protocols.


WebLab-Deusto VM software
~~~~~~~~~~~~~~~~~~~~~~~~~

For the password of a Virtual Machine remote managing protocol to be changed upon WebLab-Deusto's request, it is necessary to install certain software on the Virtual Machine snapshot. 
Currently, WebLab-Deusto provides a Vino password changer for Linux and a Remote Desktop and UltraVNC password changer for Windows.


Safety
~~~~~~

The power this system gives to the user is significant, as it grants potentially full access to a Virtual Machine. 
However, WebLab-Deusto uses the snapshot system provided by most Virtual Machine software to reset the machine to a predefined state before every use. 
Thus, though during the available time the user is free to use the hard disk or even break the system, no changes will be permanent. 
Hence, from that viewpoint, these experiments are completely safe.

Nonetheless, as usual, the experiment developer will need to be aware not to add experiment-specific risks and vulnerabilities.

It is also noteworthy that in the case of an unmanaged experiment, this is slightly more important. Though the network traffic of a managed experiment goes through the WebLab server and may hence be easily logged, users connect to the Virtual Machine directly. Consequently, though there is still a certain degree of logging and accountability through the standard WebLab login, reservation and experiment start-up mechaniams, obtaining information about the exact usage of the experiment is not possible anymore.





Creating a new VM based experiment
============================================

In this section we will create and deploy a new VM based experiment.

Though the process is rather long and it will be described in detail, it is advisable to read everything carefully, and to carry out and check each
step before following to the next.

Our goal here will be to deploy a new VM experiment, with the following characteristics:

	* Will use VirtualBox as a VM engine.
	* The VM will run a Windows OS.
	* Users will access the VM through RDP (Remote Desktop Protocol).
	
.. Note:: 
	WebLab-Deusto supports several VM OSs (Windows, Linux-likes, etc.) and a few access protocols (VNC, RDP). Setting up a
	VM with those other OSes and protocols is beyond the scope of this guide. However, the process would be very similar and
	only a few changes would be needed.

.. Warning::
	To make sure you are always on the right track, we are providing a **checklist** at the start and/or end of some sections.
	Upon encountering such a checklist, please **check carefully every point** before going on.


Prerrequisites
~~~~~~~~~~~~~~


WebLab-Deusto instance
----------------------

Before being able to create a new VM based experiment, and before being able to start following this guide, 
you will need to have a *working instance* of WebLab-Deusto. 

.. TO-DO: Find out whether we can link another sphinx document in an easier / prettier way.

If you do not have a working instance yet, you can find out how to create it in `first steps`_.

.. _first steps: https://weblabdeusto.readthedocs.org/en/latest/first_steps.html#first-steps

.. Warning::
	**CHECKLIST** *(Ensure the following before skipping to the next section)*
	
	#. I have a WebLab-Deusto instance.
	#. My WebLab-Deusto instance is successfully deployed.
	#. I have tested at least one experiment in my WebLab-Deusto instance, and it is working fine.


VirtualBox
-----------

**Oracle VM VirtualBox** is a virtualization engine. It will be the engine under which the machine
with our experiment will be run.
 
You may download the VirtualBox software package from the `virtualbox downloads`_ website, and install it normally.

.. _virtualbox downloads: https://www.virtualbox.org/wiki/Downloads
 
Once installed, some further actions are required. 

In order for WebLab-Deusto to be able to properly interact with VirtualBox, certain utilities that come with VirtualBox
need to be accessible from the command line. To do this:

	#. Locate the VirtualBox installation folder. Often, this will be `c:\\Program Files\\Oracle\\VirtualBox` or similar. 
	   Go to that location through the windows file explorer, and make sure the VirtualBox files are there. Copy that exact
	   path to that folder to your clipboard (through ctrl+c).
	
	#. We will now need to add that folder to our windows PATH environment variable. To do this under Windows 7, open the
	   *system properties* dialog. Go to *advanced settings* and then to *environment variables*. Among *system variables*
	   you will find a variable named **PATH**. Modify it, and append the VirtualBox path. Make sure a semicolon 
	   separates it from the last path in the variable.
	   
.. Warning::
	**CHECKLIST** *(Ensure the following before skipping to the next section)*
	
	#. I have successfully installed *Oracle VirtualBox*
	#. VBoxManage is accessible. To check this: Open a Windows console terminal. Type `vboxmanage -v` and hit enter.
	   If it **is** accessible, a version number should appear (such as `4.1.12`). If an error occurs, then it
	   **is not** accessible, and the previous steps should be redone.


Virtualized Windows machine
---------------------------

We now have *Oracle VirtualBox* installed. However, we do not really have a *Virtual Machine* yet. We will create one now.
In order to do this, we will require a copy of any version of Windows with RDP support. Windows XP is recommended, though later versions of
Windows should also work.

.. Note:: 
	Make sure that the Windows version you want to install supports the Remote Desktop server. Users will connect to the Virtual Machine through Remote Desktop, so 
	this is particularly important. *Professional* and higher versions support the Remote Desktop server, but certain lower versions as well. If in doubt,
	check your specific version. You can check through the official Microsoft website, or by checking whether the `enable remote access` option exists
	in your `system properties`.

We can have our copy either in CD/DVD form, or in .ISO image form (other image formats supported by VirtualBox are also fine). 

Once we have it, create the VM by following these broad steps:

	#. Start *Oracle VirtualBox*
	#. Hit the *New* button on the toolbar. A wizard dialog should pop up.
	#. Go on in the dialog. Eventually, you will be asked to write a name for your VM. Give whichever name you want.
	   This name will identify the VM, and we will later refer to it. In this guide, we will refer to is as the *VM name*.
	   Choose also the right settings for the *Operative System* and *Version* fields. The exact values will depend upon
	   the version of Windows you wish to install.
	#. Go on. The next screens should be rather straightforward. Make sure to give enough RAM to your Virtual Machine (at least 512
	   MB is probably advisable, though it depends on the version you are installing, on the experiment you want to place on it, and on
	   the real machine you will be running the Virtual Machine from). Make sure to give it enough Hard Disk space as well. Depending
	   again on the circumstances, a good minimum would probably be 10gb-20gb.
	#. Eventually the wizard will let you select the installation media. Depending on whether you want to install Windows from your
	   CD/DVD drive, or from a .ISO image, you will need to configure it appropriately. 
	#. After setting the right installation media and proceeding, the Virtual Machine should start. If it doesn't, start it manually (Virtual Machines appear
	   in VirtualBox on the left. Yours should appear there, with the *VM name* you chose). 
	#. If the VM starts, and after a while the Windows Setup appears, then congratulations, you are on the right track. If nothing happens, or if the VM
	   starts but no installation media is found, then check the previous steps (particularly, make sure you configured the installation media right, and 
	   that your CD or ISO image is right).
	#. Install Windows normally. 
	#. Once Windows is installed, make sure the Internet can be accessed from the Virtual Machine. 
	

Congratulations. If everything went ok, you now have a virtual windows machine on your VirtualBox.

.. Warning::
	**CHECKLIST** *(Ensure the following before skipping to the next section)*
	
	#. My Windows VM appears in VirtualBox. (Generally, on the left).
	#. My Windows VM can be started through VirtualBox, and the virtualized Windows seems to work fine. 
	#. I can access the Internet from the virtualized Windows.
	#. My virtualized Windows supports the Remote Desktop server. You can check whether the `enable remote access` option exists
	   in your `system properties`. (If you check this way, enable remote access now, and you will save a step for later).
	

	
Installing the WebLab In-VM Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. Warning::
	**CHECKLIST** *(Before proceeding to this section, please check the following. Feel free to skip those checks you have done already.)*
	
	#. I have a working, Windows VM which uses VirtualBox as its engine.
	#. My Windows VM supports Remote Desktop server.
	#. I can access the Internet from my Windows VM.
	#. My virtualized Windows supports the Remote Desktop server. You can check whether the `enable remote access` option exists
	   in your `system properties`. (If you check this way, enable remote access now, and you will save a step for later).
	#. The terminal command VBoxManage is accessible. To check this: Open a Windows console terminal. Type `vboxmanage -v` and hit enter.
	   If it **is** accessible, a version number should appear (such as `4.1.12`). If an error occurs, then it
	   **is not** accessible, and the previous steps should be redone.

What is the Manager?
--------------------

Users will access the virtualized Windows machine through the RDP protocol (that is, Windows' Remote Desktop). 
So that only one user (the one who has a reservation) can access the machine at a given time, a different, unique,
random password will be provided for each session. 

This means that somehow, something will need to change the password of the virtualized Windows each session.

That is the mission of the WebLab In-VM Manager.

The WebLab In-VM Manager is a service which will run within the virtualized Windows, and its main purpose will be
to receive password change requests from WebLab. 

Because as of now, the VM you have created does not yet have such a service, we will need to install it.


Manager Prerrequisites
----------------------

.NET Framework 3.5
^^^^^^^^^^^^^^^^^^

The In-VM Manager requires the Microsoft .NET Framework version 3.5. 
The In-VM Manager is meant to run within the Windows VM, so it is that machine, and not your physical, host machine, 
which needs to have it installed.

You may download Microsoft .NET Framework 3.5 from the official Microsoft website. It is advisable that you download
it from the Windows VM itself. Once downloaded, install it.

Some versions of Windows may come with .NET Framework 3.5 pre-installed. That is, however, likely not the case.


Making the VM accessible
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuring the network
.......................

The VM needs to be accessible from the host machine through an IP address, so the VM network settings will need to be 
configured properly.

Especifically, the host machine will need to connect to two ports on the windows Virtual Machine:

	* Remote Desktop port (3389). The port end users will connect to. VM will need to accept connections to it from the Internet. 
	* In-VM Manager port (6791). The WebLab-Deusto server will connect to it and command a password change when needed. 
	
.. Warning:: RDP port needs to be accessible from the Internet. Otherwise, end-users will not be able to connect to the machine.
			 The VM Manager port, however, **should only** be accessible from the host machine. Otherwise, an attacker could
			 change the password of the VM at will. Note that, however, the security risk isn't high. An attacker could gain
			 temporary control over the VM (which will last until the next experiment session begins, and the VM is reset). 
			 However, the host system itself would not be compromised.

To open the *network settings* dialog:

	#. Go to VirtualBox administrator dialog (the one with the VM list on the left)
	#. Right click on the windows VM
	#. Go to *settings*
	#. When the *settings* dialog appears, go to *network*
	
There are essentially two ways to configure the network:

	#. **NAT**: The VM will connect to the Internet through the host machine's connection. In order for it to work, you would 
	   need to forward port 3389 and 6791 properly. That is not particularly hard, but isn't trivial either, so NAT **is not
	   recommended**.
	#. **Bridged Adapter**: The VM will connect to the Internet directly. This **is the recommended** way. The Windows VM will be given
	   its own IP on your local network. If your local network doesn't support DHCP, further configuration may be needed.
	   
It is hence suggested that you choose *Bridged Adapter*.

.. Note:: You might need to restart the VM before network configuration changes take effect.	

.. Note:: From this point, this guide will assume that you are indeed using a *Bridged Adapter* network. 


Checking the network config
...........................

If the network was properly configured, the virtualized Windows:

	* Will still have Internet access
	* Will have been assigned an IP in the local network
	
We will now find out which IP has been assigned to the VM.

There are several ways to do this. The easiest is (everything is done on the virtualized Windows):

	* Open a terminal (a command line)
	* Type `ipconfig`
	
You will see a list of every network adapter in your machine, along with its IP addresses.
The adapter we seek is our standard `Local Network Ethernet Connection` (or a similar name).
The IP we seek is the `IPv4 address`.
Write out that IP address. From now on, we will refer to that IP as the *VM IP*.

.. Note:: An example of a valid IP would be `192.168.1.105`, or any LAN IP. An example of an *invalid* IP would be `localhost` or `127.0.0.1`. 
		  Often, but not always, an IP that starts with `10` won't be valid either. If any of this happens, and further checks are unable to
		  access the VM, then re-check your network settings.
		  
We should now be able to access our VM through the VM IP. 

Our first check will be the following:

	#. Start a command line. 
	#. Type `ping <VM IP>` on it. Replace <VM IP> with your actual VM IP. For instance: `ping 192.168.1.105`. Hit enter.

If timeout errors appear, then the test failed. Your VM, for some reason, is not reachable through that IP. Check the previous steps.
If, however, ping does send several packets, and certain times appear on the screen, then congratulations, your machine, for now,
seems to be reachable.

We will now carry out yet another check. In your host machine (not your VM one) open the Windows Remote Desktop client.
Try to connect to the VM IP. It should work. If it doesn't:

	#. Check that the version of Windows that the VM is running supports the Remote Desktop server.
	#. Check (in the VM) that remote access is enabled.
	#. Check this section again and ensure that the network is configured properly.
	
	
.. Warning::
	**CHECKLIST** *(Ensure the following before skipping to the next section)*
	
	#. My guest Windows (virtualized Windows) supports Microsoft .NET Framework 3.5
	#. My guest Windows can be accessed through Remote Desktop from my host Windows







