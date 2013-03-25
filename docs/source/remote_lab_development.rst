.. _remote_lab_development:

Remote laboratory development
=============================

.. note::
    **This section is being written at this time (March 2013)**

    You may go to the `old documentation site
    <http://code.google.com/p/weblabdeusto/wiki/Latest_ExperimentDeveloperGuide>`_,
    but you must be aware that some APIs have changed for this version. So
    please use the mailing list.

.. contents:: Table of Contents

Introduction
------------

This section covers the development of new remote laboratories using
WebLab-Deusto. As detailed in :ref:`technical_description`, WebLab-Deusto
provides a set of libraries so experiment developers can create their own remote
laboratories.

There are two major approaches for using WebLab-Deusto:

#. Managed laboratories (prefered)
#. Unmanaged laboratories

Which are described below.

Managed laboratories
^^^^^^^^^^^^^^^^^^^^

Managed laboratories are those laboratories developed with the API of
WebLab-Deusto. They basically have two parts:

* A client, developed using one of the libraries provided by WebLab-Deusto (see
  :ref:`below <managed_libraries_client>`).
* A server, developed using one of the provided server libraries or using
  XML-RPC directly (see :ref:`below <managed_libraries_server>`).

This way, the client will run on the web browser and will basically display the
user interface. Whenever the user interface requires accessing the equipment, it
will use the provided API to submit a command and retrieve a response. For
example, a typical application might perform an action when the user presses a
button. This button will submit a message (command) using the API, and
WebLab-Deusto will call a particular method in the server side with that
particular message.

Therefore, managed laboratories count with the following advantages:

* Experiment developer does not manage any type of communications. The client
  API has a method for submitting a command, which the WebLab-Deusto client will
  propagate as securely as the system has been configured (e.g. supporting SSL)
  to the server, which once in the campus side, the server will submit the
  command to the particular equipment (regardless where it is deployed in the
  internal topology of the campus side network). All commands submitted through
  WebLab-Deusto will go through pure HTTP, crossing firewalls and proxies.
* All the information is stored in the database by default, so it is possible to
  perform learning analytics. By default, administrators and instructors be able
  to track what exact commands were submitted by the student. This process
  however does not add a relevant latency, since instead of storing each command
  whenever is sent, it adds it to a memory queue (which is a fast operation),
  and other thread is continuosly retrieving information from the queue and
  storing it in the database in a batch basis.
* Managed laboratories support local load balancing. This means that if you ever
  have multiple copies of a laboratory, if the communication goes through the
  WebLab-Deusto API, the client will not need to know which copy is being
  addressed, since the WebLab-Deusto internals will forward the message to the
  laboratory used by the current user.

Given the amount of technologies used in remote laboratories, WebLab-Deusto not
only supports but even provides libraries to support multiple programming
languages. 

Unmanaged laboratories
^^^^^^^^^^^^^^^^^^^^^^

However, not everybody in the remote laboratory community is comfortable with
developing a remote laboratory from scratch by programming. For this reason,
WebLab-Deusto also supports unmanaged laboratories, which are those where the
communication is not sent through WebLab-Deusto, but directly to the final
server.

The two clear examples of this are:

#. Virtual Machines based remote laboratories. A VirtualBox (at this moment)
   virtual machine created by the experiment developer is loaded. The virtual
   machine might run a Linux or Windows system, which will be accessed through
   SSH, VNC or Remote Desktop. WebLab-Deusto guarantees that the server will be
   executed.
#. LabVIEW Remote Panels. They were developed but they caused too many problems.
   If you are really interested, contact us and we can create more
   documentation on their support in WebLab-Deusto. But at this stage, it simply
   does not make too much sense. It is much better if you support :ref:`LabVIEW
   as managed <managed_library_server_labview>`.

The main drawbacks of unmanaged laboratories is that:

* They might cause problems with proxies or firewalls, since the communication
  is managed by the final system.
* The user tracking functionality is decreased: WebLab-Deusto still registers
  who uses what and when, but not what the user did during the session.
* The load balancing functionality is decreased or even removed.

Additionally, this is more complex to deploy for system administrators.

For these reasons, using the managed approach is desirable, while we maintain
this other approach for those laboratories which are far more difficult to
develop.

Future
^^^^^^

At the time of this writing (March 2013), we might create a new type of
unmanaged laboratory based on web frameworks (e.g. ASP.NET, Flask, Django,
etc.). Contact us if you are interested on more information or if this would be
a priority for you.

Managed laboratories
--------------------

.. _managed_libraries_client:

Client side
^^^^^^^^^^^

Introduction
............

Google Web Toolkit
..................

JavaScript
..........


Java applets
............


Flash applets
.............


.. _managed_libraries_server:

Server side
^^^^^^^^^^^

Introduction
............


Python
......


Java
....


.NET
....


C
..

C++
...

Node.js
.......


.. _managed_library_server_labview:

LabVIEW
.......

Native Python server
....................


Tools
^^^^^



Unmanaged laboratories
----------------------

Conclusions
-----------

