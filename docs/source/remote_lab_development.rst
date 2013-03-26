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

This section describes how to develop experiments using the managed model.

Introduction
^^^^^^^^^^^^

As previously defined, in the managed laboratories, all the communications are
managed by WebLab-Deusto. This basically means that, as seen on the following
figure, the client code will call a set of methods such as:

.. code-block:: java

   // In the client side
   weblab.sendCommand("press button1");

And WebLab-Deusto guarantees that this string will be forwarded to the proper
experiment server. In the experiment server, there will be a method such as (in
Java):

.. code-block:: java

    public String sendCommand(String command) throws WebLabException {
        // Manage the command and return the results
        if (command.startsWith("press ")) {
            String what = command.substring("press ".length);
            pressButton(what);
            return getStatus();
        }
    }

So as to do this, WebLab-Deusto provides :ref:`APIs for the client
<managed_libraries_client>`, which wrap the communications submitting the
commands to the server side using HTTP (and HTTPS if available), adding the
required metadata (such as the session identifier). This is *step 1* in the
following figure. Once in the Core server (check :ref:`the technical description
if lost <technical_description>`), it checks if that the session is still
available and with an experiment assigned.  If so, it submits the command to the
Laboratory server in charge of the assigned experiment (there might be different
laboratory servers) and stores the command in the database. This process is
faster than it may sound, since it uses memory structures and internal queues so
there is only a single thread using the database for adding the commands
submitted. This is *step 2* in the figure. Once in the Laboratory server, it
checks to which Experiment server the command should be submitted, and submits
it (this is *step 3*). If the Experiment Server was developed with one of the
:ref:`libraries for servers <managed_libraries_server>`, then this gets the
message in the programming language used and passes it to the Experiment server
code.

.. figure:: /_static/managed_model.png
   :align: center

   Command sent through the managed model. See the diagram `in full size here <_static/managed_model.png>`_.

This way, it is entirely up to the experiment developer to choose the proper
programming environment for its experiments. Furthermore, developers will select
the format of the contents submitted as commands. WebLab-Deusto does not impose
any restriction on this side, so developers may send a simple string such as
``press button1`` that will later parse, or they may use an XML or JSON format.

For this reason, in the case of the managed model, developers do not need to handle:

* Scheduling (the core server manages it)
* Communications (the libraries manage it)
* User tracking (every command is stored in the database)
* Complex deployments (e.g. load balancing: it is configured at WebLab-Deusto
  level)


.. _managed_libraries_client:

Client side
^^^^^^^^^^^

In this section, the client side libraries and approaches for developing remote
laboratories are presented.

Introduction
............

The client code is focused on two tasks:

* Providing the user interface
* Submitting commands to the Experiment server and managing the responses

While WebLab-Deusto supports some web libraries, it is highly recommended to use
libraries which rely on JavaScript (such as JavaScript itself or Google Web
Toolkit). Those laboratories developed on top of these libraries will be
available for mobile devices, and the number of conflicts in different platforms
will be highly decreased, since they will not need any plug-in installed.

In the following sections describe how to use each of the provided APIs.

Google Web Toolkit
..................

.. note::

   To be written (March 2013).


JavaScript
..........

.. note::

   To be written (March 2013).


Java applets
............

.. note::

   To be written (March 2013).

Flash applets
.............

.. note::

   To be written (March 2013).

.. _managed_libraries_server:

Server side
^^^^^^^^^^^

This section covers how to develop the server side of a remote laboratory using the WebLab-Deusto Managed model.

Introduction
............

There are two ways to develop a remote laboratory using the WebLab-Deusto API in the managed model:

* Using Python (which is the programming language used by the rest of the
  WebLab-Deusto system) as a native laboratory (therefore managing even the
  configuration through WebLab-Deusto).
* Running an external process which acts as a XML-RPC server. We provide
  libraries for doing this automatically, described below.

In this case, there is no prefered way to develop the laboratories, whatever is
easier for the developer.

All the libraries can be found in the repository, in the
`experiments/managed/libs/server
<https://github.com/weblabdeusto/weblabdeusto/tree/master/experiments/managed/libs/server>`_
directory.


WebLab-Deusto server (Python)
.............................

.. note::

   To be written (March 2013).


Java
....

.. note::

   To be written (March 2013).



The Java library can be found in the `experiments/managed/libs/server/java
<https://github.com/weblabdeusto/weblabdeusto/tree/master/experiments/managed/libs/server/java>`_
library. It is an `Eclipse <http://www.eclipse.org/>`_ project, so you should be
able to import it if you are using this IDE. Otherwise, you can use `ant
<http://ant.apache.org/>`_ to compile it, by running::

   $ ant build 
   $ ant run

The structure of the source code is the following::

   + src
     + es/deusto/weblab/experimentservers
       + exceptions
         - (defined exceptions)
       - ExperimentServer.java
       - Launcher.java
       - (Other auxiliar classes)
     + com/example/weblab
       - DummyExperimentServerMain.java
       - DummyExperimentServer.java

There, the important classes are those available in the package ``es.deusto``.
The ones in the ``com.example`` can be removed and replaced by the proper
package of your application. They are there as a working example of what the
interface is.

The two important classes are ``ExperimentServer`` and ``Launcher``. The former
is a class which defines all the optional methods which can be implemented by
the experiment developer (e.g. a method for receiving commands). The latter is a
class that will start a XML-RPC server taking an instance of the class generated
by the experiment developer.

Then, you can use:

.. code-block:: java

    public class DummyExperimentServerMain {
        public static void main(String [] args) throws Exception{
            IExperimentServer experimentServer = new DummyExperimentServer();
            Launcher launcher = new Launcher(10039, experimentServer);
            launcher.start();
        }
    }



.NET
....

.. note::

   To be written (March 2013).


C
..

.. note::

   To be written (March 2013).


C++
...

.. note::

   To be written (March 2013).


Node.js
.......

.. note::

   To be written (March 2013).


.. _managed_library_server_labview:

LabVIEW
.......

.. note::

   To be written (March 2013).

Python
......

.. note::

   To be written (March 2013).



Tools
^^^^^

.. note::

   To be written


Unmanaged laboratories
----------------------

Virtual machines
^^^^^^^^^^^^^^^^

.. note::

   To be written

Conclusions
-----------

.. note::

   To be written

