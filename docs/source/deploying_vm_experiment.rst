.. _toctree-directive:
.. _deploying_vm_experiment:

Virtual Machines based remote labs
==================================

Introduction
------------

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
^^^^^^^^^^^^^^^^^^^^^^^^^^

Virtual Machine experiments work differently than traditional Managed experiments. A Virtual Machine experiment does not include any WebLab-specific code. 
Instead, the experiment is developed anyhow and deployed on a Virtual Machine image. WebLab-Deusto then manages that Virtual Machine. 
WebLab-Deusto users will, upon experiment startup through the standard WebLab-Deusto web, receive a password. Then, they may use that password to connect to the 
Virtual Machine through either Remote Desktop or VNC. From then on, the user can freely use the Virtual Machine and the experiment deployed on it. 
Once the time has run out, WebLab-Deusto will close the Virtual Machine and restore it to a pre-defined snapshot before the next use.


Supported Virtual Machine, OSes, and Protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently WebLab-Deusto VM system has been tested on Linux, under which the VNC protocol through the TightVNC server (and compatible clients) is supported. 
It has also been tested on Windows, under which both UltraVNC and Remote Desktop are supported.

The Virtual Machine software currently supported is Virtual Box.

It is noteworthy that this list is likely to be extended in the future, and that the system is easily extensible, so it would not be particularly hard for a developer to add support to new 
VM software or new Protocols.


WebLab-Deusto VM software
^^^^^^^^^^^^^^^^^^^^^^^^^

For the password of a Virtual Machine remote managing protocol to be changed upon WebLab-Deusto's request, it is necessary to install certain software on the Virtual Machine snapshot. 
Currently, WebLab-Deusto provides a Vino password changer for Linux and a Remote Desktop and UltraVNC password changer for Windows.


Safety
^^^^^^

The power this system gives to the user is significant, as it grants potentially full access to a Virtual Machine. 
However, WebLab-Deusto uses the snapshot system provided by most Virtual Machine software to reset the machine to a predefined state before every use. 
Thus, though during the available time the user is free to use the hard disk or even break the system, no changes will be permanent. 
Hence, from that viewpoint, these experiments are completely safe.

Nonetheless, as usual, the experiment developer will need to be aware not to add experiment-specific risks and vulnerabilities.

It is also noteworthy that in the case of an unmanaged experiment, this is slightly more important. Though the network traffic of a managed experiment goes through the WebLab server and may hence be easily logged, users connect to the Virtual Machine directly. Consequently, though there is still a certain degree of logging and accountability through the standard WebLab login, reservation and experiment start-up mechaniams, obtaining information about the exact usage of the experiment is not possible anymore.



Creating a new VM based experiment
----------------------------------

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
^^^^^^^^^^^^^^


WebLab-Deusto instance
""""""""""""""""""""""

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
""""""""""

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
"""""""""""""""""""""""""""

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
	#. Apart from whichever administrator account you create, create a second admin account called `weblab`. Naming it `weblab` is important. 
	#. Once Windows is installed, make sure the Internet can be accessed from the Virtual Machine. 
	
	
.. Note:: 
	The `weblab` account we created in previous steps could actually be named differently. But then, additional configuration changes would be required
	in the In-VM Manager (which we will install in later sections of this guide), and for simplicity, these won't be covered here.
	

Congratulations. If everything went ok, you now have a virtual windows machine on your VirtualBox.

.. Warning::
	**CHECKLIST** *(Ensure the following before skipping to the next section)*
	
	#. My Windows VM appears in VirtualBox. (Generally, on the left).
	#. My Windows VM can be started through VirtualBox, and the virtualized Windows seems to work fine. 
	#. I can access the Internet from the virtualized Windows.
	#. My virtualized Windows supports the Remote Desktop server. You can check whether the `enable remote access` option exists
	   in your `system properties`. (If you check this way, enable remote access now, and you will save a step for later).
	

	
Installing the WebLab In-VM Manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
""""""""""""""""""""

Users will access the virtualized Windows machine through the RDP protocol (that is, Windows' Remote Desktop). 
So that only one user (the one who has a reservation) can access the machine at a given time, a different, unique,
random password will be provided for each session. 

This means that somehow, something will need to change the password of the virtualized Windows each session.

That is the mission of the WebLab In-VM Manager.

The WebLab In-VM Manager is a service which will run within the virtualized Windows, and its main purpose will be
to receive password change requests from WebLab. 

Because as of now, the VM you have created does not yet have such a service, we will need to install it.


Manager Prerrequisites
""""""""""""""""""""""

**.NET Framework 3.5**

The In-VM Manager requires the Microsoft .NET Framework version 3.5. 
The In-VM Manager is meant to run within the Windows VM, so it is that machine, and not your physical, host machine, 
which needs to have it installed.

You may download Microsoft .NET Framework 3.5 from the official Microsoft website. It is advisable that you download
it from the Windows VM itself. Once downloaded, install it.

Some versions of Windows may come with .NET Framework 3.5 pre-installed. That is, however, likely not the case.


**Making the VM accessible**

*Configuring the network*

The VM needs to be accessible from the host machine through an IP address, so the VM network settings will need to be 
configured properly.

Especifically, the host machine will need to connect to two ports on the windows Virtual Machine:

	* Remote Desktop port (3389). The port end users will connect to. VM will need to accept connections to it from the Internet. 
	* In-VM Manager port (6789). The WebLab-Deusto server will connect to it and command a password change when needed.
	
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
	   its own IP on your local network. If your local network doesn't support DHCP, further configuration may be needed. Note, however,
	   that choosing this configuration means that the Guest and Host machines will communicate through your local network directly.
	   If your local network is somehow restricted or filtered by a firewall, this may lead to issues (See the third note).
	   
It is hence suggested that you choose *Bridged Adapter*.

.. Note:: You might need to restart the VM before network configuration changes take effect.	

.. Note:: From this point, this guide will assume that you are indeed using a *Bridged Adapter* network.

.. Note:: Choosing the Bridged Adapter configuration means that the communication between the Host and the Guest machine will be
          carried out through the local network. If your local network is restricted or filtered by a firewall, problems may arise.
          If you do indeed have a firewall, you will need to make sure that port 3389 (RDP) and port 6789 (communication between Guest
          and Host) are open. Port 3389 is easy to test, as you can assume that if RDP works, the port is open. Port 6789
          is harder to test, and if it is being blocked, you will only notice later on this guide, when you carry out the
          suggested tests. If the firewall can't be turned off or configured, then you could also use **NAT** instead of **Bridged Adapter**.
          Though the concept is similar, using **NAT** is not fully covered in this guide. The only difference, however, should be
          that you would need to configure *Port Forwarding* within the Virtual Box configuration, so that you can access the required
          ports from the Host machine.



*Checking the network config*

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
	#. My guest Windows can be accessed through Remote Desktop from my host Windows.
	#. The firewall on my local network should not prevent access to port 6789.



Installing the In-VM Manager itself
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Deploying the binaries*


Locate the In-VM Manager binaries. All WebLab distributions should include them. 
If %WEBLAB% is the WebLab folder, then the binaries we seek should be in:
`%WEBLAB%\\experiments\\unmanaged\\vm_services\\WindowsVM\\WindowsVMService\\bin\\Release`

Place those binaries into your guest Windows. For instance, you may place them into
the `c:\\vmservice` folder (create it, it won't exist).

*Installing as a service*

The Manager will run as a Windows service. To install it, you can't execute WindowsVMService.exe
straightaway. Instead, you should execute the `sc_install_service.bat` script.
If your VM is running a relatively modern version of Windows you should right click on the script
and **run as administrator**.

.. Warning:: If you do not run the script with administrator priviledges, it will be unable to
			 install it properly.

If for any reason `sc_install_service.bat` failed, you may try with `install_service.bat`, though this
is not recommended.

When those succeed, your service will be installed as a standard Windows service, and can be
started and stopped as one. Alternatively, `sc_start_service` and `sc_stop_service` scripts
are provided, but they probably will only work if the service was installed through `sc_install_service`.

Before going on, check whether your service is indeed installed.

Open the windows *Service Manager* by running `services.msc` (hit [WINKEY]+R to be able to run programs).

Among the services there, a new one, `WeblabVMService`, should appear. If it doesn't, do not go on, as
something went wrong.

*Starting the service*

Locate the service in the Windows *Service Manager*. If the service is not started already, then click on
it and start it.

.. Note:: Alternatively, if you installed the service through the `sc_install_service` script, you may
		  use the `sc_start_service` and the `sc_stop_service` to start and stop it.

If for any reason it fails to start, then something went wrong. Do not go on. Verify that you have .NET 3.0, 
and that the service is installed properly. 

*Testing the service*

.. Warning::
	**CHECKLIST** *(Ensure the following before starting this section. All of them apply to the **guest** Windows (virtualized one))*
	
	#. WeblabVMService appears in my list of processes (which can be checked through the Windows' *services.msc* utility).
	#. When I start WeblabVMService, no errors occur. The status of the service changes to *started* and stays so.
	
We will now carry out a few tests to check whether WeblabVMService is working as expected with our current settings.

**Test 1**
This test should be done within the guest OS. That is, within the virtualized Windows. *(This test is meant to check that
the In-VM Manager is working properly and can change the local password).*

	#. If the WeblabVMService is not running already, start it.
	#. Open a browser window.
	#. Do the following query: `http://localhost:6789/?sessionid=testone`
	#. It should take a while and then take you to a blank page with only the word `Done` written in black. If the 
	   page cannot be loaded or if an error occurs, then the service is either not running or failing. If that is the case, do not proceed. It is 
	   suggested that you contact the developers for support. From this point on, we will assume `Done` was printed.
	#. The password of your Windows `weblab` account has now been changed to `testone`. That is essentially what the previous query did.
	   You should now verify that this is indeed the case. Logout and try to login into your `weblab` account, using `testone` as password.
	#. If you manage to login using that password, then congratulations, the first test was successful, you may go on. If you can't login
	   using that password, then something failed. If `done` was printed to the screen, this is fortunately unlikely. Make sure you 
	   followed every step right. If it still doesn't work, please contact the developers for support.
	   
	   
**Test 2**
This test assumes that the first test was successful. We will try the following, *(This test is meant to check that the In-VM
Manager can indeed be accessed and used from the Host machine).*

	#. If the WeblabVMService is not running already, start it.
	#. Find out the IP that has been assigned to your Virtual Machine in your local network. This is the IP we used
	   in previous sections to connect to the machine through RDP. It will most likely be something such as `192.168.100.5`, but it
	   may start with `172` instead, or with other digits.
	#. Open a browser in your **host** machine (that is, **not** your guest machine). 
	#. Do the following query: `http://192.168.100.5:6789/?sessionid=testtwo`. Replace 192.168.100.5 with your actual VM IP.
	#. It should take you to the same page as in the first test. A blank page with `Done` in black. If it worked, congratulations. The
	   second test was successful. You may try to login with the password `testtwo` into the `weblab` account of your Virtual Machine
	   if you wish to be sure. If it didn't, see the following note.
	   
.. Note:: The previous test should have loaded a blank page with `Done` written in black. If it did, you may skip this note. If it didn't,
		  something went wrong. Most often, this means that the guest OS is not accessible from the host OS. Try to login into your host
		  OS through RDP, in the same way you did before when you configured the *network settings* of the VM (in previous sections of this guide).
		  If you still can connect to the machine through RDP, then you should repeat the first test, to make sure the service is still working.
		  If RDP is working, and the first test is working, but the second test is still failing, please make sure that you have no firewall which may
		  be blocking port 6789 on your local network (see the previous *network settings* section if you do). You may also try to repeat the second test with a different
		  browser. If it still does not work, please :ref:`contact <contact>` the developers for support. (In this guide, from this point, we will assume that
		  the second test did work. If it didn't, you may not want to proceed until the issue is solved).
		  
Congratulations, if you are here, both tests should have passed. This means that WeblabVMService is properly installed and working.


.. Warning::
	**CHECKLIST** *(Ensure the following before going on to the next section.)*

	#. Test 1 was completed and works as expected.
	#. Test 2 was completed and works as expected.


Preparing the Virtual Machine: Base Snapshot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

What is a snapshot?
"""""""""""""""""""

Most VM systems (such as VirtualBox) support snapshots. Snapshots describe the exact state of the Virtual Machine at a given point of time.
Once you have taken a shapshot, you can at any time restore your VM to it. This is how WebLab-Deusto VM experiment ensures that any change
a user makes to the VM, is restored before the next session.

Base Snapshot
"""""""""""""

We will take an snapshot, which will be our `base snapshot`, the one every user will get to use. After the user is done,
WebLab-Deusto will restore the system to that same `base snapshot` again.

To prepare a first base snapshot, you can follow these steps:

	#. Start your guest Windows.
	#. Login into your `weblab` account.
	#. Start the In-VM Manager if it is not running already.
	#. Install any software you wish the users to have.
	#. Open any program that you want the users to see.
	#. Prepare everything for the user. Arrange every open window. 
	#. Your machine should now be ready. Without closing it, it's time to take a snapshot. In VirtualBox menu, go to
	   Machine->Take a snapshot. It will let you choose a name. Type `base`. You can actually choose a different one and configure
	   it later, but we will use `base` for simplicity.
	  
.. Note:: Probably, your actual experiment is not ready yet. When it is, you will probably have to modify the base snapshot to include it.
		  Fortunately, that is easy. Though the previous steps are somewhat linear, really the only important things are:
		  
			#. Your guest windows needs to be logged in the `weblab` account.
			#. The In-VM manager needs to be started.
			#. The machine must be turned on when you take the snapshot. If it isn't, it will have to be boot-up everytime, and this
			   takes too long of a time. 
		
		  These are essentially the three points that you have to take into account when creating your own base snapshots.
		  
Testing the Base Snapshot
"""""""""""""""""""""""""

We will make sure we are on the right track. Do the following:

	#. Start your guest Windows.
	#. In your guest Windows, create some new file, and add it to the desktop. It can be any file, and have any name. For instance,
	   you may create a `TESTING.TXT` text file.
	#. From this point on, we will use the command line, to ensure that it is working as expected too.
	#. Open a command line in your **host** Windows. (That is, not on your virtualized Windows). We will use it to manage virtualbox.
	#. Recall your `VM name`. As we established in previous sections of this guide, that is the name that appears in VirtualBox's list,
	   and which you can right click to start the machine, etc.
	#. Type the following command in the command line: `vboxmanage controlvm "Windows VM" poweroff`. You should replace `Windows VM` with your
	   actual `VM name`. The following is what should happen::
	   
		C:\Users\lrg>vboxmanage controlvm "Windows VM" poweroff
		Oracle VM VirtualBox Command Line Management Interface Version 3.2.10
		(C) 2005-2010 Oracle Corporation
		All rights reserved.

		0%...10%...20%...30%...40%...50%...60%...70%...80%...90%...100%

	   Your machine should turn off. If it doesn't, make sure you installed VirtualBox properly, as described in previous sections, and that you
	   specified the right `VM name` in your command.
	   
	#. We will now restore the `base` snapshot using the command line. Type the following: `vboxmanage snapshot "Windows VM" restore "base"`.
	   Replace *Windows VM* with the actual name of your Virtual Machine, and replace *base* with the actual name of your snapshot (which is most likely *base*
	   too, if you followed the previous sections accurately). The following is what should happen::
	   
	    C:\Users\lrg>vboxmanage snapshot "Windows VM" restore "base"
		Oracle VM VirtualBox Command Line Management Interface Version 3.2.10
		(C) 2005-2010 Oracle Corporation
		All rights reserved.
		
	#. Finally, we will start the VM through the command line. Type the following: `vboxmanage startvm "Windows VM"`.
	   Again, replace *Windows VM* with the actual name of your Virtual Machine. The Virtual Machine should appear, loading your 
	   virtualized Windows, and the following should appear in your console::
	
		C:\Users\lrg>vboxmanage startvm "Windows VM"
		Oracle VM VirtualBox Command Line Management Interface Version 3.2.10
		(C) 2005-2010 Oracle Corporation
		All rights reserved.
		
	#. If an error occurs, something is wrong. Check the previous steps. Note that your Windows snapshot should have loaded. What you see is exactly
	   what your experiment users will see. If something is amiss, for instance, if Windows had to boot (if it wasn't started already) or if
	   the programs you left open when you created your `base` snapshot are not open anymore, then you probably did not create the snapshot
	   properly or you did not restore it. You might want to check the previous sections if that is the case.
	   
	

.. Warning::
	**CHECKLIST** *(Please ensure the following before going on to the next section)*
	
	#. My VM was loaded properly. Windows did not need to boot. 
	#. The programs I left open when I created my `base` snapshot were there still.
	#. I was able to accomplish all of the above through the command line.

If nothing went wrong, congratulations, your snapshot is ready.




Configuring the WebLab instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have followed the guide up to here, every prerrequisite is now ready. In this last section, we will configure and test the WebLab
experiment itself. That is, the experiment server which will actually control the VM we have created, through the means we have provided.


Recalling important variables
"""""""""""""""""""""""""""""

Before going on we will need to remember some variables which we established during the previous sections. We need the following:

	#. **VM name**: The name you gave to your VM. The one you used with the *vboxmanage* commands. 
	#. **VM ip**: The local IP of your VM. That is the IP that you used to connect to it through RDP.
	
	
Creating the instance through Weblab-admin
""""""""""""""""""""""""""""""""""""""""""

As we mentioned in the first sections of this guide, you need to have the weblab-admin script properly installed.
The next steps assume you do.

We will next use weblab-admin to create a new WebLab instance with our VM experiment. We will run the following command::

	weblab-admin create WLTest --vm --vbox-base-snapshot "base" --vbox-vm-name "Windows VM" --vm-estimated-load-time 30 
	--http-query-user-manager-url "http://192.168.64.143:6789" --vm-url 192.168.64.143 --http-server-port 8000
	
However, you will need to make a few changes to the command:

	#. Change the IP, 192.168.64.143 for your **VM ip**. You need to change it for the http-query-user-manager-url, which is,
	   essentially, the address to which the password changing queries that we have explained in previous sections are sent.
	   You also need to change it for the vm-url variable. This isn't that important, because it is simply the URL that will
	   be displayed to experiment users, so that they can connect through RDP.
	#. Change the Virtual Machine name, "Windows VM", for your own **VM name**.
	#. Note that VMDeploy is, in this case, the name we have given to our new instance. You may change it, if you want to.
	

This is what should happen::

	(weblab.dev) C:\shared\weblab_github\weblabdeusto_lrg\server\src>weblab-admin
	create WLTest --force --vm --vbox-base-snapshot base --vbox-vm-name "Windows VM" 
	--vm-estimated-load-time 30 --http-query-user-manager-url "http://192.168.64.143:6789"
	--vm-url 192.168.64.143 --http-server-port 8000

	patchZsiPyExpat skipped; ZSI not installed
	patchZsiFaultFromException skipped; ZSI not installed

	Congratulations!
	WebLab-Deusto system created

	Run:

		 weblab-admin start VMTestTwoS

	to start the WebLab-Deusto system. From that point, you'll be able to access:

	   http://localhost:8000/

	Or in production if you later want to deploy it in Apache:

		 http://localhost/weblab/

	And log in as 'admin' using 'password' as password.

	You should also configure the images directory with two images called:

		 sample.png and sample-mobile.png

	You can also add users, permissions, etc. from the admin CLI by typing:

		weblab-admin admin VMTestTwoS

	Enjoy!
	

If an error occurs here, it is likely that it is not related to the VM experiment. Please, make sure that you have installed weblab 
properly and that you can deploy instances (without vm experiments) through *weblab-admin*. Unfortunately, doing that is
beyond the scope of this guide, but you can check the weblab installation documentation. From this point, we will assume
your instance was deployed properly.


Testing our new instance
""""""""""""""""""""""""

To start our new instance, type the following::

	weblab-admin start WLTest
	
Replace `WLTest` with the name you gave to your weblab instance (which is most likely `WLTest` either way.

Your WebLab instance should now start. 

Open a browser in your computer, and connect to it through http://localhost:8000, which is the port we specified.

You can log into it with the account name `admin` and the password `password`. There should be a few experiments, among
them, your new VM experiment.

Check, reserve, and check whether it works as expected.

If the experiment is reserved properly, and you can connect to your Virtual Machine through RDP using the provided address, and if you can see
the snapshot we set in previous sections. **Congratulations, you have successfully deployed an VM experiment!**

If no error occurred, this guide is **over**. 

If something went wrong, take a look at the next section.


Something failed
""""""""""""""""

If you are in this section, some problem occurred and your VM deployment is not working. We will here describe some likely errors. 

*My experiment seems to work properly, but I can't connect through RDP to the provided address.*

Make sure that the IP that you are being provided with is the same as the IP you tested with, on the `network configuration` section of this guide.
If it is and the `network configuration` section's test still succeeds, please :ref:`contact <contact>` the Weblab developers for support.

*The VM experiment appears, but an error occurs before the reservation succeeds.*

Make sure that you installed Weblab properly. That is, make sure that experiments other than the VM one work. If other experiments don't work,
then the problem is most likely not related to VMs. Check the weblab installation guide. If it's only the VM experiment which does not work,
then please :ref:`contact <contact>` the Weblab developers for support.

*The VM experiment appears, I can reserve, but when the experiment loads, the progress bar never finishes.*

Make sure that you have installed the In-VM Manager properly by carrying out every suggested test and checklist. Particularly, make sure that
you can change your Guest's password from your Host machine through http://{guest-ip}/?sessionid=newpassword.
Check the console in case there is an error. If there is, please :ref:`contact <contact>` the Weblab developers for support. 






