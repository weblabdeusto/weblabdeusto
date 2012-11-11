.. _toctree-directive:
.. _deploying_vm_experiment:

Introduction
===========

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







