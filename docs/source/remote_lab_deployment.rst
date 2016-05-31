.. _remote_lab_deployment:

Remote laboratory deployment
============================

.. contents:: Table of Contents

Introduction
------------

In the :ref:`previous section <remote_lab_development>` we have covered how to
create new remote laboratories using the WebLab-Deusto APIs. After it, you have
a working (yet draft or very initial) code that you want to use. However, we
have not covered how to use them in an existing deployment of WebLab-Deusto.
This section covers this task. This way, here we will see how to register the
already developed clients and servers.

.. figure:: /_static/weblab_deployment.png
   :align: center
   :width: 600px

   Steps to deploy a remote laboratory in WebLab-Deusto.


This process is compounded of the following steps:

#. :ref:`remote_lab_deployment_deploy_experiment_server`
#. :ref:`remote_lab_deployment_register_in_lab_server`
#. :ref:`remote_lab_deployment_register_scheduling`
#. :ref:`remote_lab_deployment_add_to_database`

After these steps, your laboratory should be working. If you have any trouble,
check the :ref:`remote_lab_deployment_troubleshooting` section.

.. _remote_lab_deployment_deploy_experiment_server:

Step 1: Deploying the Experiment server
---------------------------------------

As :ref:`previously explained <remote_lab_development>`, there are two major
ways to develop a WebLab-Deusto Experiment server:

#. :ref:`Managed <remote_lab_deployment_managed>`, which includes Experiment servers developed in Python, as well as
   experiments developed in other platforms (e.g., Java, .NET, LabVIEW, C,
   C++...)

   #. If the Experiment server was developed in Python, then it might use any of the protocols of WebLab-Deusto. This part is explained below in :ref:`remote_lab_deployment_deploy_python_server`.
   #. However, if other platform was used (e.g., Java, .NET, C, C++), then the XML-RPC approach must be taken.  This is explained below in :ref:`remote_lab_deployment_deploy_xmlrpc_server`.

#. :ref:`Unmanaged <remote_lab_deployment_unmanaged>`, such as external HTTP applications. 

This section assumes that you have previously read the following two sections:

* :ref:`directory_hierarchy`
* :ref:`technical_description`

.. _remote_lab_deployment_managed:

Managed server
^^^^^^^^^^^^^^

This section describes how to deploy a laboratory using the managed approach.

   #. If the Experiment server was developed in Python, then it might use any of the protocols of WebLab-Deusto. This part is explained below in :ref:`remote_lab_deployment_deploy_python_server`.
   #. However, if other platform was used (e.g., Java, .NET, C, C++), then the XML-RPC approach must be taken.  This is explained below in :ref:`remote_lab_deployment_deploy_xmlrpc_server`.

.. _remote_lab_deployment_deploy_python_server:

WebLab-Deusto Python server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As explained in :ref:`directory_hierarchy`, WebLab-Deusto uses a directory
hierarchy for configuring how the communications among different nodes is
managed. In the case of WebLab-Deusto Python servers, you may run them inside
the same process as the Laboratory server, being able to use the configuration
subsystem and being easier to manage.

So as to do this, let us assume that there is a simple system as the one created
by::

    weblab-admin create sample --http-server-port=12345

And that you have developed an experiment using the Python API as explained in :ref:`remote_lab_development_weblab_python`. Your experiment can be something as simple as:

.. code-block:: python

   import json

   from weblab.experiment.experiment import Experiment
   import weblab.experiment.level as ExperimentApiLevel

   class ElectronicsLab(Experiment):
        def __init__(self, coord_address, locator, config, *args, **kwargs):
            super(ElectronicsLab,self).__init__(*args, **kwargs)
            self.config = config

        def do_start_experiment(self, client_initial_data, server_initial_data):
            print("Start experiment")
            print("Client initial data:", json.loads(client_initial_data))
            print("Server initial data:", json.loads(server_initial_data))
            print("Camera:", self.config.get('my_camera_url'))
            return json.dumps({ "initial_configuration" : "cam='cam1'"})

        def do_get_api(self):
            return ExperimentApiLevel.level_2

        def do_dispose(self):
            print("User left")
            return "{}"
        
        def do_send_command_to_device(self, command):
            print("Command: ", command)
            return "Got your command"

        def do_should_finish(self):
            print("Checking if the user should exit. If returned 0, will not ask again. If return 1, WebLab will kick him out")
            return 5



Let us also assume that this code is in a file called ``myexperiments.py``, and that is in a directory called ``/home/tom/experiments``.

Then, first, we will need to make sure that WebLab-Deusto can access that file.
To this end, we would add that directory to the ``PYTHONPATH``. 

In Windows we can run the following each time before running weblab-admin.py start::

   (weblab) C:\Users\Tom> set PYTHONPATH=C:\Users\Tom\experiments

In Linux / Mac OS X we can run the following::

   (weblab) tom@tom-laptop:~$ export PYTHONPATH=/home/tom/experiments:$PYTHONPATH

To verify that this is correct, you should be able to do the following::

   $ python
   [...] 
   >>> import myexperiments
   >>> 

If no ImportError occurs, it means that everything required (e.g., your code and WebLab-Deusto code) is available.

.. warning::

   The ``PYTHONPATH`` path must be absolute (e.g., ``/home/tom/experiments``) and not
   relative (e.g.,  ``../experiments``). When running ``weblab-admin.py start``, the
   current working directory is changed and could lead to wrong results.

In this case, the Python class identifier of your Python laboratory would be ``myexperiments.ElectronicsLab`` (since it's the class ``ElectronicsLab`` of the module ``myexperiments.py``). If you had a more complex hierarchy (for example: a Python package called ``myinstitution`` and inside several modules like ``myexperiments.py``), then the Python class identifier would be ``myinstitution.myexperiments.ElectronicsLab``.

The next step is to modify the ``configuration.yml`` file generated by ``weblab-admin.py create sample``. Originally, it looks like the following:

.. code-block:: yaml

    hosts:
      core_host:
        runner: run.py
        config_file: core_host_config.py
        processes:
          core_process1:
            components:
              core:
                config:
                  core_facade_port: 10000
                  core_facade_server_route: route1
                type: core
          laboratory1:
            components:
              experiment1:
                class: experiments.dummy.DummyExperiment
                config:
                  dummy_verbose: true
                type: experiment
              laboratory1:
                config_file: lab1_config.py
                protocols:
                  port: 10001
                type: laboratory

Which looks like the following:

.. figure:: /_static/weblab_deployment_python_1.png
   :align: center
   :width: 500px

   ``sample`` as created by default

But we want to add a new laboratory called ``electronics`` so it becomes the following:

.. figure:: /_static/weblab_deployment_python_2.png
   :align: center
   :width: 500px

   ``sample`` after the modification


So as to have this new component which is an experiment running your code, you have to add it inside the ``components`` of ``laboratory1``, as follows:

.. code-block:: yaml

    hosts:
      core_host:
        runner: run.py
        config_file: core_host_config.py
        processes:
          core_process1:
            components:
              core:
                config:
                  core_facade_port: 10000
                  core_facade_server_route: route1
                type: core
          laboratory1:
            components:
              experiment1:
                class: experiments.dummy.DummyExperiment
                config:
                  dummy_verbose: true
                type: experiment
              electronics:
                class: myexperiments.ElectronicsLab
                type: experiment
              laboratory1:
                config_file: lab1_config.py
                protocols:
                  port: 10001
                type: laboratory

If you want to add configuration variables, then you can either add them to the component or to any of the upper layers (to the host, process or globally), and either add them in a configuration file or inline as follows:

.. code-block:: yaml

    hosts:
      core_host:
        runner: run.py
        config_file: core_host_config.py
        processes:
          core_process1:
            components:
              core:
                config:
                  core_facade_port: 10000
                  core_facade_server_route: route1
                type: core
          laboratory1:
            components:
              experiment1:
                class: experiments.dummy.DummyExperiment
                config:
                  dummy_verbose: true
                type: experiment
              electronics:
                class: myexperiments.ElectronicsLab
                config:
                  my_camera_url: http://cams.weblab.deusto.es/webcam/electronics.jpg
                type: experiment
              laboratory1:
                config_file: lab1_config.py
                protocols:
                  port: 10001
                type: laboratory

From the Python code, you may access that variable.

From this point, the internal WebLab-Deusto address of your Experiment server is
``electronics:laboratory1@core_host``. You might see it later when seeing which
device was accessed by students, or in logs.

However, refer to :ref:`directory_hierarchy` for further details for more
complex deployments. 

.. warning::

    Avoid naming conflicts with your laboratory name. For instance,
    ``myexperiments.ElectronicsLab`` relies on the fact that there is no other
    ``myexperiments`` directory in the ``PYTHONPATH``. If you use other names,
    such as ``experiments.ElectronicsLab``, ``voodoo.ElectronicsLab`` or
    ``weblab.ElectronicsLab``, you will enter in naming conflicts with existing
    modules of WebLab-Deusto or of libraries used by WebLab-Deusto.


To verify that the configuration is fine, start the server::

    $ weblab-admin.py start sample
     * Running on http://0.0.0.0:12345/ (Press CTRL+C to quit)
    Press <enter> or send a sigterm or a sigint to finish
     

If no error is reported in a few seconds, you can press enter to stop it and continue. If the
following error appears::

    $ weblab-admin.py start sample
     * Running on http://0.0.0.0:12345/ (Press CTRL+C to quit)
    Press <enter> or send a sigterm or a sigint to finish
    [...]
    voodoo.gen.exc.LoadingError: Error loading component: 'myexperiments.ElectronicsLab' for server electronics:laboratory1@core_host: No module named myexperiments

It means that the myexperiments.py file does not seem to be available. Verify
that running in the same terminal reports no error::

   $ python
   [...]
   >>> import myexperiments
   >>> print(myexperiments.ElectronicsLab)
   <class 'myexperiments.ElectronicsLab'>
   >>> 

If it reports an ImportError, verify that you configured the ``PYTHONPATH``
according to what it was defined earlier in this subsection.

After you start WebLab-Deusto with no error, you can now jump to the :ref:`remote_lab_deployment_register_in_lab_server`.

.. _remote_lab_deployment_deploy_xmlrpc_server:

Non-Python managed servers (XML-RPC based)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As explained in :ref:`directory_hierarchy`, WebLab-Deusto uses a directory
hierarchy for configuring how the communications among different nodes is
managed. In the case of experiments using XML-RPC, it is required to *lie the
system*, by stating that there is an experiment server listening through XML-RPC
in a particular port, with a particular configuration that will never be run.

The easiest way to see an example of this configuration is running the following::

    weblab-admin.py create sample --xmlrpc-experiment --xmlrpc-experiment-port=10039 --http-server-port=12345

This will generate a particular configuration, with two *hosts* at
WebLab-Deusto level: one called ``core_host``, and the other ``exp_host``.
So as to run the first one, you should run::

    weblab-admin.py start sample -m core_machine

You may also run::

    weblab-admin.py start sample -m exp_machine

In other console at the same time. That way, there would be a Python Experiment
server listening on port ``10039``. However, this is not what we want here. What
we want here is to be able to run other laboratories, such as a Java or .NET
Experiment server. So if we don't execute this last command, and instead we run
our Java (or .NET, C++, C...) application listening in that port, everything
will work.

For this reason, using the ``weblab-admin`` command with those arguments is the
simplest way to get a laboratory running. If you only want to test the system
with your new developed remote laboratory, you can simply use the
``--xmlrpc-experiment`` flags and skip to the next section.

However, the typical action is to use the :ref:`directory_hierarchy`
documentation to establish at WebLab-Deusto level that there will be an
Experiment server listening in a particular port.

So, let's start from scratch. Let's imagine that we create other example, such
as::

    weblab-admin create sample --http-server-port=12345

We want to add an external Experiment server. We will first create a new
*machine*, by modifying ``sample/configuration.xml`` to look like this:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <machines
            xmlns="http://www.weblab.deusto.es/configuration" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="global_configuration.xsd" >

        <machine>core_machine</machine>
        <!-- Add a new machine exp_machine -->
        <machine>exp_machine</machine>

    </machines>

We will create that directory (``exp_machine``), and we will add a new file inside called ``configuration.xml``:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <instances
            xmlns="http://www.weblab.deusto.es/configuration" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="machine_configuration.xsd" >

        <instance>exp_instance</instance>

    </instances>

In this directory, we will create such a directory called ``exp_instance``, which will also have the following ``configuration.xml``:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <servers 
        xmlns="http://www.weblab.deusto.es/configuration" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="instance_configuration.xsd">

        <user>weblab</user>

        <server>experiment1</server>
    </servers>

On it, we will create that directory (``experiment1``), which will have a single file called ``configuration.xlm`` as follows:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <server
        xmlns="http://www.weblab.deusto.es/configuration" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.weblab.deusto.es/configuration server_configuration.xsd"
    >

        <configuration file="server_config.py" />

        <type>weblab.data.server_type::Experiment</type>
        <methods>weblab.methods::Experiment</methods>

        <implementation>experiments.dummy.DummyExperiment</implementation>

        <protocols>
            <protocol name="Direct">
                <coordinations>
                    <coordination></coordination>
                </coordinations>
                <creation></creation>
            </protocol>
            <protocol name="XMLRPC">
                <coordinations>
                    <coordination>
                        <parameter name="address" value="127.0.0.1:10039@NETWORK" />
                    </coordination>
                </coordinations>
                <creation>
                    <parameter name="address" value="127.0.0.1"     />
                    <parameter name="port"    value="10039" />
                </creation>
            </protocol>
        </protocols>
    </server>

Note that the port number is repeated twice (one for creating the server, which
we will never do, and the other for informing the rest of the WebLab-Deusto
servers how to access the Experiment server).

Doing this, the Experiment server will have been created. You only need to be
sure that you start the Experiment server every time you start the WebLab-Deusto
servers (preferibly, just before than just after).

In the following sections, you will address the Experiment server as
``experiment1:exp_instance@exp_machine``.

.. warning::

    When this is specified:

    .. code-block:: xml

        <parameter name="address" value="127.0.0.1:10039@NETWORK" />

    Then, WebLab-Deusto will attempt to perform XML-RPC requests to
    ``http://127.0.0.1:10039/``.

    However, certain libraries (such as the one of .NET) does not support this
    scheme, and it requires that WebLab-Deusto calls
    ``http://127.0.0.1:10039/weblab``. For this reason, in .NET and LabVIEW, you
    need to configure the system using:

    .. code-block:: xml

        <parameter name="address" value="127.0.0.1:10039/weblab@NETWORK" />


You can now jump to the :ref:`remote_lab_deployment_register_in_lab_server`.

.. _remote_lab_deployment_unmanaged:

Unmanaged server
^^^^^^^^^^^^^^^^

Foo bar


You can now jump to the :ref:`remote_lab_deployment_register_in_lab_server`.

.. _remote_lab_deployment_register_in_lab_server:

Step 2: Registering the experiment server in a Laboratory server
----------------------------------------------------------------

In the following figure, we have already finished steps 1 and 2, which are the
most complex. The rest of the steps are independent of the technology used, and
they are only focusing on registering the laboratory in the different layers. In
this subsection, we're in the step 3: registering the server in the Laboratory
server.

.. figure:: /_static/weblab_deployment.png
   :align: center
   :width: 600px

   We're in step 3.


Each Experiment Server must be registered in a single Laboratory server. One
Laboratory Server can manage multiple Experiment servers. So as to register a
Experiment server, we have to go to the Laboratory server configuration file.
When you create a WebLab-Deusto instance doing::

   $ weblab-admin create sample

This file is typically in ``core_machine`` -> ``laboratory1`` -> ``laboratory1``
-> ``server_config.py``, and by default it contains the following:

.. code-block:: python

    laboratory_assigned_experiments = {
            'exp1:dummy@Dummy experiments' : {
                    'coord_address' : 'experiment1:laboratory1@core_machine',
                    'checkers' : ()
                },
        }

This means that the current laboratory has one Experiment server assigned. The
identifier of this Experiment server is ``exp1:dummy@Dummy experiments``, which
means ``exp1`` of the Experiment ``dummy`` of the category ``Dummy
experiments``. It is located in the server ``experiment1`` in the *instance*
``laboratory1`` in the ``core_machine``. You can find in
:ref:``<directory_hierarchy_multiple_servers>`` more elaborated examples.

So as to add the new experiment, you must add a new entry in that dictionary.
For example, if you have added two different laboratories of electronics, and in
the previous step you have located them in the ``laboratory1`` instance in the
``core_machine``, you should edit this file to add the following:

.. code-block:: python

    laboratory_assigned_experiments = {
            'exp1:dummy@Dummy experiments' : {
                    'coord_address' : 'experiment1:laboratory1@core_machine',
                    'checkers' : ()
                },
            'exp1:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:laboratory1@core_machine',
                    'checkers' : (),
                    'api'      : '2',
                },
            'exp1:electronics-lesson-2@Electronics experiments' : {
                    'coord_address' : 'electronics2:laboratory1@core_machine',
                    'checkers' : (),
                    'api'      : '2',
                },
        }

If you have used XML-RPC (i.e., any of the libraries which is not Python) and
the experiment server is somewhere else outside the ``core_machine``, you only
need to change the ``coord_address``. For example, if you created a new
laboratory using Java, you will need to add something like:

.. code-block:: python

    laboratory_assigned_experiments = {
            'exp1:dummy@Dummy experiments' : {
                    'coord_address' : 'experiment1:laboratory1@core_machine',
                    'checkers' : ()
                },
            'exp1:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2'
                },
        }

The ``api`` variable indicates that the API version is ``2``. If in the future
we change the Experiment server API, the system will still call your Experiment
server using the API available at this time.

One of the duties of the Laboratory server is to check frequently whether the
Experiment server is alive or not. This may happen due to a set of reasons, such
as:

* The laboratory uses a camera which is broken
* The connection failed
* The Experiment server was not started or failed

By default, every few seconds the system checks if the communication with the
Experiment server works. If it is broken, it will notify the administrator (if
the mailing variables are configured) and will remove it from the queue. If it
comes back, it marks it as fixed again.

However, you may customize the ``checkers`` that are applied. The default
checkers are defined in ``weblab.lab.status_handler`` (`code
<https://github.com/weblabdeusto/weblabdeusto/tree/master/server/src/weblab/lab/status_handler.py>`_).
At the time of this writing, there are two:

* ``HostIsUpAndRunningHandler``, which opens a TCP/IP connection to a particular
  host and port. If the connection fails, it marks the experiment as broken.
* ``WebcamIsUpAndRunningHandler``, which downloads an image from a URL and
  checks that the image is a JPEG or PNG.

So as to use them, you have to add them to the ``checkers`` variable in the
Laboratory server configuration. For example, if you have a FPGA laboratory with
a camera and a microcontroller that does something, you may have the following:

.. code-block:: python

    'exp1:ud-fpga@FPGA experiments' : {
        'coord_address' : 'fpga:process1@box_fpga1',
        'checkers' : (
                        ('WebcamIsUpAndRunningHandler', ("https://www.weblab.deusto.es/webcam/proxied.py/fpga1",)),
                        ('HostIsUpAndRunningHandler', ("192.168.0.70", 10532)),
                    ),
        'api'      : '2',
    },

In this case, the system will check from time to time that URL to find out an
image, and will connect to that port in that IP address, as well as the default
checking (calling a method in the Experiment server to see that it is running).

You can develop your own checkers in Python, inheriting the
``AbstractLightweightIsUpAndRunningHandler`` class and adding the class to the
global ``HANDLERS`` variable of that module.

Additionally, if you have laboratories that you don't want to check, you may use
the following variable in the Laboratory server. It will simply skip this.

.. code-block:: python

    laboratory_exclude_checking = [
        'exp1:electronics@Electronics experiments',
        'exp1:physics@Physics experiments',
    ]


.. _remote_lab_deployment_register_scheduling:

Step 3: Registering a scheduling system for the experiment
----------------------------------------------------------

Now we move to the Core server. The Core server manages, among other features,
the scheduling of the experiments. At the moment of this writing, there are
different scheduling options (federation, iLabs compatibility, and priority
queues). We do not support booking using a calendar at this moment.

All the configuration of the Core server related to scheduling is by default in
the ``core_machine/machine_config.py`` file. It is placed there so if you have 4
Core servers in different instances (:ref:`which is highly recommended
<performance>`), you have the configuration in a single location. In this file,
you will find information about the database, the scheduling backend, etc.

The most important information for registering a remote laboratory is the following:

.. code-block:: python

    core_scheduling_systems = {
            'dummy'            : ('PRIORITY_QUEUE', {}),
            'robot_external'   : weblabdeusto_federation_demo,
    }

Here, it is defined the different schedulers available for each remote
laboratory *type*. WebLab-Deusto supports load balancing, so it assumes that
you may have multiple copies of a remote laboratory. In that sense, we will
say that one *experiment type* might have multiple *experiment instances*.
This variable (``core_scheduling_systems``) defines which scheduling system
applies to a particular *experiment type*. Say that you have one of two copies
of a experiment identified by ``electronics`` (of category ``Electronics
experiments``). Then you will add a single *experiment type* to this variable:

.. code-block:: python

    core_scheduling_systems = {
            'dummy'            : ('PRIORITY_QUEUE', {}),
            'robot_external'   : weblabdeusto_federation_demo,
            'electronics'      : ('PRIORITY_QUEUE', {}),
    }

However, we still have to map the different experiment instances to this
experiment type. So as to do this, you will see that there is another variable
in the Core server which by default it has: 

.. code-block:: python

    core_coordinator_laboratory_servers = {
        'laboratory1:laboratory1@core_machine' : {
                'exp1|dummy|Dummy experiments' : 'dummy1@dummy',
            },
    }

This variable defines which Laboratory servers are associated, which
*experiment instances* are associated to each of them, and how they are related
to the scheduling system. For instance, with this default value, it is stating
that there is a Laboratory server located at ``core_machine``, then in
``laboratory1`` and then in ``laboratory1``. This Laboratory server manages a
single experiment server, identified by ``exp1`` of the experiment type
``dummy`` of category ``Dummy experiments``. This *experiment instance*
represents a slot called ``dummy1`` of the scheduler identified by ``dummy``.

So, when a user attempts to use an experiment of type ``dummy`` (category
``Dummy experiments``), the system is going to look for how many are available.
It will see that there is only one slot (``dummy1``) in the queue (``dummy1``)
that is of that type. So if it is available, it will call that Laboratory server
asking for ``exp1`` of that *experiment type*.

Therefore, if you have added a single Experiment server of electronics to the
existing Laboratory server, you can safely add:

.. code-block:: python

    core_coordinator_laboratory_servers = {
        'laboratory1:laboratory1@core_machine' : {
                'exp1|dummy|Dummy experiments'             : 'dummy1@dummy',
                'exp1|electronics|Electronics experiments' : 'electronics1@electronics',
            },
    }

Load balancing
^^^^^^^^^^^^^^

If you have two copies of the same type of laboratory, you can add:

.. code-block:: python

    core_coordinator_laboratory_servers = {
        'laboratory1:laboratory1@core_machine' : {
                'exp1|dummy|Dummy experiments'             : 'dummy1@dummy',
                'exp1|electronics|Electronics experiments' : 'electronics1@electronics',
                'exp2|electronics|Electronics experiments' : 'electronics2@electronics',
            },
    }

This means that if two students come it asking for an ``electronics``
laboratory, one will go to one of the copies and the other to the other. The
process is random. A third user would wait for one of these two students to
leave.

If you have two different experiments (one of electronics and one of physics), then you should add:


.. code-block:: python

    core_coordinator_laboratory_servers = {
        'laboratory1:laboratory1@core_machine' : {
                'exp1|dummy|Dummy experiments'             : 'dummy1@dummy',
                'exp1|electronics|Electronics experiments' : 'electronics1@electronics',
                'exp1|physics|Physics experiments'         : 'physics1@physics',
            },
    }

Sharing resources among laboratories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


This system is quite flexible. For instance, it becomes possible to have more
than one Experiment server associated to the same physical equipment. For
example, in WebLab-Deusto we have the CPLDs and the FPGAs, with one Experiment
server that allows users to submit their own programs. However, we also have
other Experiment servers called ``demo``, which are publicly available and
anyone can use them. These Experiment servers do not allow users to submit their
own program, though: they use their own default program for demonstration
purposes. Additionally, we have two CPLDs, so the load of users is balanced
between these two copies, and a single FPGA. The configuration is the following:

.. code-block:: python

    core_coordinator_laboratory_servers = {
        'laboratory1:laboratory1@core_machine' : {

                # Normal experiments:
                'exp1|ud-pld|PLD experiments'    : 'pld1@pld',
                'exp2|ud-pld|PLD experiments'    : 'pld2@pld',
                'exp1|ud-fpga|FPGA experiments'  : 'fpga1@fpga',

                # Demo experiments: note that the scheduling side is the same
                # so they are using the same physical equipment.
                'exp1|ud-demo-pld|PLD experiments' : 'pld1@pld',
                'exp2|ud-demo-pld|PLD experiments' : 'pld2@pld',
                'exp1|ud-demo-fpga|FPGA experiments' : 'fpga1@fpga',
            },
    }

In this case, if three students reserve ``ud-pld@PLD experiments``, two of them
will go to the two copies, but the third one will be in the queue. If somebody
reserves a ``ud-demo-pld@PLD experiments``, he will also be in the queue, even
if the laboratory and the code that he will execute is different. The reason is
that it is using the same exact device, so it makes sense decoupling the
scheduling subsystem of the experiment servers and clients.

.. _remote_lab_deployment_concurrency:

Concurrency
^^^^^^^^^^^

Finally, one feature of this system is that it enables that you provide more
than one time slot to a single resource. For example, you may establish at Core
server that there are 10 different ``copies`` of the laboratory, even if there
is a single one:

.. code-block:: python

    core_coordinator_laboratory_servers = {
        'laboratory1:laboratory1@core_machine' : {
                'exp1|dummy|Dummy experiments'             : 'dummy1@dummy',
                'exp1|electronics|Electronics experiments' : 'electronics1@electronics',
                'exp2|electronics|Electronics experiments' : 'electronics2@electronics',
                'exp3|electronics|Electronics experiments' : 'electronics3@electronics',
                'exp4|electronics|Electronics experiments' : 'electronics4@electronics',
                'exp5|electronics|Electronics experiments' : 'electronics5@electronics',
            },
    }

Then, in the Laboratory server you must create those registries, but they can
point to the same laboratory:

.. code-block:: python

    laboratory_assigned_experiments = {
            'exp1:dummy@Dummy experiments' : {
                    'coord_address' : 'experiment1:laboratory1@core_machine',
                    'checkers' : ()
                },
            'exp1:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2'
                },
            'exp2:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2'
                },
            'exp3:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2'
                },
            'exp4:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2'
                },
            'exp5:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2'
                },
        }

This way, five students will be able to enter to the laboratory at the same
time, and they will be able to interact each other. The main problem is that by
default, the API does not support knowing which student is submitting each
request, since the methods are essentially something like::

    String sendCommand(String command);

However, there is other API, called the Concurrent API, not supported at the
moment by most of the libraries but yes by the Python experiments, which
supports this. It which basically adds a ``lab_session_id`` string to the
beginning of each parameter. That way, the method for sending commands, for
instance, is as follows::

    String sendCommand(String labSessionId, String command);

Using this, the Experiment developer can identify who is accessing in the
laboratory and reply different messages to each user. So as to configure this,
the Laboratory server must use the following: 

.. code-block:: python

    laboratory_assigned_experiments = {
            'exp1:dummy@Dummy experiments' : {
                    'coord_address' : 'experiment1:laboratory1@core_machine',
                    'checkers' : ()
                },
            'exp1:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2_concurrent'
                },
            'exp2:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2_concurrent'
                },
            'exp3:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2_concurrent'
                },
            'exp4:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2_concurrent'
                },
            'exp5:electronics-lesson-1@Electronics experiments' : {
                    'coord_address' : 'electronics1:exp_instance@exp_machine',
                    'checkers' : (),
                    'api'      : '2_concurrent'
                },
        }


.. _remote_lab_deployment_add_to_database:

Step 4: Add the experiment server to the database and grant permissions
-----------------------------------------------------------------------

At this point, we have the Experiment server running, the Experiment client
configured, the Laboratory has registered the Experiment server and the Core
server has registered that this experiment has an associated scheduling scheme
(queue) and knows in which Laboratory server it is located.

Now we need to make it accessible for the users. The first thing is to register
the remote laboratory in the database. Go to the administrator panel by clicking
on the top right corner the following icon:

.. image:: /_static/click_on_admin_panel.png
   :width: 300 px
   :align: center


You will see this:

.. image:: /_static/weblab_admin.jpg
   :width: 650 px
   :align: center

On it, go to ``Experiments``, then on ``Categories``, and then on ``Create``.
You will be able to add a new category (if it did not exist), such as
``Electronics experiments``, and click on Submit:

.. image:: /_static/add_experiment_category.png
   :width: 450 px
   :align: center


Then, go back to ``Experiments``, then ``Experiments``, and then on ``Create``.
You will be able to add a new experiment, such as ``electronics``, using the
category just created. The Start and End dates refer to the usage data. At this
moment, no more action is taken on these data, but you should define since when
the experiment is available and until when:

.. image:: /_static/add_new_experiment.png
   :width: 450 px
   :align: center


At this moment, the laboratory has been added to the database. Now you can
guarantee the permissions on users. So as to do this, click on ``Permissions``,
``Create``. Select that you want to grant permission to a Group, of permission
type ``experiment_allowed``.

.. image:: /_static/weblab_admin_grant_permission1.jpg
   :width: 450 px
   :align: center

And then you will be able to grant permissions on the developed laboratory to a
particular group (such as Administrators):

.. image:: /_static/weblab_admin_grant_permission_on_electronics.jpg
   :width: 450 px
   :align: center

From this point, you will be able to use this experiment from the main user
interface.


JavaScript
^^^^^^^^^^
.. note::

    To be written (June 2016).

Java applets
^^^^^^^^^^^^

In the case of Java applets, the identifier is simply ``java``. However, so as
to load a particular laboratory, some additional parameters must be configured,
such as where is the JAR file, what class inside the JAR file must be loaded,
and the size of the applet. An example of this configuration would be:

.. code-block:: javascript

  "java": [
       {
           "experiment.name": "javadummy",
           "experiment.category": "Dummy experiments",

           "jar.file": "WeblabJavaSample.jar",
           "code"  : "es.deusto.weblab.client.experiment.plugins.es.deusto.weblab.javadummy.JavaDummyApplet",

           "height": 350,
           "width": 500,

           "message": "This is a message displayed on top of the experiment client",
           "experiment.picture": "/img/experiments/java.jpg",


           "experiment.info.description": "description",
           "experiment.info.link": "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Java_Dummy"
       }
    ]

Once again, let us assume that you have 2 laboratories developed in Java
applets, one of physics and other of electronics. You may have the following:

.. code-block:: javascript

    "experiments" : {
        "java": [
            {
               "experiment.name": "physics-1",
               "experiment.category": "Physics experiments",

               "jar.file": "PhysicsApplet.jar",
               "code"  : "edu.example.physics.PhysicsApplet",

               "height": 350,
               "width": 500,

               "experiment.picture": "/img/experiments/physics.jpg"
           },
           {
               "experiment.name": "electronics-1",
               "experiment.category": "Electronics experiments",

               "jar.file": "ElectronicsApplet.jar",
               "code"  : "edu.example.physics.ElectronicsApplet",

               "height": 350,
               "width": 500,

               "experiment.picture": "/img/experiments/electronics.jpg"
           }
        ]
    }

Those JAR files should be located in the ``public`` directory (`see here
<https://github.com/weblabdeusto/weblabdeusto/tree/master/client/src/es/deusto/weblab/public>`_),
which will require you to re-compile and re-run the ``setup`` script.

Flash
^^^^^

In the case of Flash applications, the identifier is simply ``flash``. However, so as
to load a particular laboratory, some additional parameters must be configured,
such as where is the SWF file, the size of the application, or the maximum time
that WebLab-Deusto will wait to check if the Flash applet has been connected
-e.g., 20 seconds-, since sometimes the user uses a flash blocking application
or a wrong version of Adobe Flash. An example of this configuration would be:

.. code-block:: javascript

    "flash": [
        {
            "experiment.name": "flashdummy",
            "experiment.category": "Dummy experiments",

            "flash.timeout": 20,
            "swf.file": "WeblabFlashSample.swf",

            "height": 350,
            "width": 500,

            "message": "This is a message that will be loaded before the applet",
            "page.footer": "This message will be loaded under the flash applet",

            "experiment.picture": "/img/experiments/flash.jpg",

            "experiment.info.description": "description",
            "experiment.info.link": "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Flash_Dummy"
        }
    ]

Once again, let us assume that you have 2 laboratories developed in Flash
applets, one of physics and other of electronics. You may have the following:

.. code-block:: javascript

    "experiments" : {
        "flash": [
            {
               "experiment.name": "physics-1",
               "experiment.category": "Physics experiments",

               "swf.file": "PhysicsLab.swf",

               "height": 350,
               "width": 500,

               "experiment.picture": "/img/experiments/physics.jpg"
           },
           {
               "experiment.name": "electronics-1",
               "experiment.category": "Electronics experiments",

               "swf.file": "ElectronicsLab.swf",

               "height": 350,
               "width": 500,

               "experiment.picture": "/img/experiments/electronics.jpg"
           }
        ]
    }

Those SWF files should be located in the ``public`` directory (`see here
<https://github.com/weblabdeusto/weblabdeusto/tree/master/client/src/es/deusto/weblab/public>`_),
which will require you to re-compile and re-run the ``setup`` script.


.. _remote_lab_deployment_troubleshooting:

Troubleshooting
---------------

Take into account the following issues:

* Everything in the client's *public* directory will not be available until you re-compile the client (``ant gwtc``) **AND** you re-install the codebase (``python setup.py install``).
* Web browsers tend to cache information. If you have changed the configuration.js document and the changes are not shown, go manually to ``/weblab/client/weblabclientlab/configuration.js``, verify if it was updated, and if not refresh the page (e.g., using Control + F5).

.. note::

    More errors will be added in this section.

In case of further errors, please :ref:`contact us <contact>`.

Summary
-------

WebLab-Deusto requires five actions to add a new experiment, explained in this
section and on this figure:

.. figure:: /_static/weblab_deployment.png
   :align: center
   :width: 600px

   Steps to deploy a remote laboratory in WebLab-Deusto.

These five actions are registering the new client by modifying the
``configuration.js`` file, deploying the new server, modifying the
configuration of the Laboratory server and the Core server and adding the
experiment to the database using the Admin panel.

After doing this, you may start sharing your laboratories with other
WebLab-Deusto deployments, as stated in the :ref:`following section
<remote_lab_sharing>`.

