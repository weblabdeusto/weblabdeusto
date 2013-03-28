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

#. :ref:`remote_lab_deployment_register_experiment_client`
#. :ref:`remote_lab_deployment_deploy_experiment_server`
#. :ref:`remote_lab_deployment_register_in_lab_server`
#. :ref:`remote_lab_deployment_register_scheduling`
#. :ref:`remote_lab_deployment_add_to_database`
#. :ref:`remote_lab_deployment_grant_permissions`

After these steps, your laboratory should be working. If you have any trouble,
check the :ref:`remote_lab_deployment_troubleshooting` section.

.. _remote_lab_deployment_register_experiment_client:

Register the experiment client
------------------------------

In WebLab-Deusto, administrators can change the name of laboratories directly. So
the client is not aware of which laboratory identifiers (e.g., "laboratory
called *pld-lesson1*) must load which client must be loaded.

So as to do this mapping, the WebLab-Deusto client has a configuration file
called ``configuration.js``. When you create a WebLab-Deusto instance::

   $ weblab-admin.py create sample

The client configuration file can be found in ``client/configuration.js``. This
file has the following structure:

.. code-block:: javascript

    {
        "development": false,
        "base.location": "",
        "host.entity.image.mobile": "/img/client/images/logo-mobile.jpg",
        "demo.available": false,
        "host.entity.image": "/img/client/images/logo.jpg",
        "create.account.visible": false,
        "experiments.default_picture": "/img/experiments/default.jpg",
        "host.entity.link": "http://www.yourentity.edu",
        "admin.email": "weblab@deusto.es",

        "experiments": {

            "gpib1": [
                {
                    "experiment.category": "GPIB experiments",
                    "experiment.name": "ud-gpib1"
                }
            ],

            "pic18": [
                {
                    "experiment.category": "PIC experiments",
                    "experiment.name": "ud-pic18",
                    "experiment.picture": "/img/experiments/microchip.jpg"
                }

            // ...
        }
    }

.. warning::

    When editing this file, do not use a comma before the end of a list or
    objects. For example, this is fine:
    
    .. code-block:: javascript

         "gpib1": [
            {
                "experiment.category": "GPIB experiments",
                "experiment.name": "ud-gpib1"
            }
         ]

    But this other code, while it will work in Google Chrome or Firefox, will
    cause an error on Microsoft Internet Explorer:

    .. code-block:: javascript

         "gpib1": [
            {
                "experiment.category": "GPIB experiments",
                "experiment.name": "ud-gpib1", // THIS COMMA
            },  // THIS COMMA
         ]

    Since you are using a comma before the '}', and because you are using a
    comma before the ']'.

As you can see, there are some global variables (e.g., ``base.location``,
``demo.available``...), but there is a special variable called ``experiments``.
This variable registers all the experiment clients, and maps them to each
experiment identifier. For instance, let us assume that there is an experiment
client identified by ``visir``, and there were three different experiments in
the database, called ``visir-lesson1``,  ``visir-lesson2`` and
``visir-lesson3``, all of them of the category ``Visir experiments``, and they
all use this client. Let us assume that there is other experiment client,
identified by ``robot-movement``, and there is a single experiment registered
for it, called ``robot-movement`` of the category ``Robot experiments``. What we
would need to configure is the following:

.. code-block:: javascript
    
    "experiments" : {

        "visir" : [

            {
                "experiment.category": "Visir experiments",
                "experiment.name": "visir-lesson1"
            },

            {
                "experiment.category": "Visir experiments",
                "experiment.name": "visir-lesson2"
            },

            {
                "experiment.category": "Visir experiments",
                "experiment.name": "visir-lesson3"
            }

        ],

        "robot-movement" : [
            {
                "experiment.category": "Robot experiments",
                "experiment.name": "robot-movement"
            }
        ]
    }

Whenever the user logs in, he will get from the server the list of laboratories
he has access to (e.g., ``visir-lesson2`` and ``robot-movement``). The client in
that moment will check this configuration file looking for which experiment
clients it must load for those laboratories.

Now, let us assume that we want to put a cool logo in the main screen, as well
as some documentation on these laboratories. We can do this by adding more
variables to each of the objects, as follows:

.. code-block:: javascript

    "experiments" : {

        "visir" : [

            {
                "experiment.category": "Visir experiments",
                "experiment.name": "visir-lesson1",
                "experiment.info.description": "description",
                "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
                "experiment.picture": "/img/experiments/visir.jpg"
            },

            {
                "experiment.category": "Visir experiments",
                "experiment.name": "visir-lesson2",
                "experiment.info.description": "description",
                "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
                "experiment.picture": "/img/experiments/visir.jpg"
            },

            {
                "experiment.category": "Visir experiments",
                "experiment.name": "visir-lesson3",
                "experiment.info.description": "description",
                "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
                "experiment.picture": "/img/experiments/visir.jpg"
            }

        ],

        "robot-movement" : [
            {
                "experiment.category": "Robot experiments",
                "experiment.name": "robot-movement",
                "experiment.info.description": "description",
                "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#robot",
                "experiment.picture": "/img/experiments/robot.jpg"
            }
        ]
    }

The file defined (``/img/experiments/``) is the ``public`` directory in the
client source. You can find it `here
<https://github.com/weblabdeusto/weblabdeusto/tree/master/client/src/es/deusto/weblab/public/img/experiments>`_.
If you add them there, remember that you have to re-compile the client manually,
by going to the client::

    $ cd client
    IN UNIX:
    $ ./gwtc.sh 
    IN WINDOWS:
    $ gwtc
    OR:
    $ ant gwtc

And run the ``setup`` script again::

    $ python setup.py install

.. note::

    This part is subject to change in the future. We now want to store this
    information in the database so as to avoid this step. The attached issue is
    `#14 <https://github.com/weblabdeusto/weblabdeusto/issues/14>`_.

Now you may be wondering: and **what is the client identifier for the laboratory I
have just implemented?** This depends on the selected technology, so go to the
proper subsection below.

Google Web Toolkit
^^^^^^^^^^^^^^^^^^

The WebLab-Deusto client is developed in Google Web Toolkit (GWT), and,
internally, all remote laboratories are developed in this technology. For
example, in the case of Java applets, there is a special type of experiment
developed in GWT which wraps the loading and the methods of the Java applet.

GWT is a technology that takes Java code and generates JavaScript code. The
linker it uses will remove any code which is never called. Therefore, it is
difficult to implement a pure plug-in system that automatically loads the
different experiment clients. For this reason, every remote laboratory client
must be registered in a global list.

This list is located in the client code, in the class
``es.deusto.weblab.client.lab.experiments.EntryRegistry``. You may find the
source code `in this directory
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/lab/experiments/EntryRegistry.java>`_.
On it, you can see that it basically collects instances of ``CreatorFactory``,
which are classes that implement the interface ``IExperimentCreatorFactory``
(`see code
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/lab/experiments/IExperimentCreatorFactory.java>`_).
These classes will only call the experiment (and therefore, they will only dowload 
the required JavaScript, CSS code and images) when the student selects that
laboratory and if he has permissions.

Once the ``CreatorFactory`` has been registered in the ``EntryRegistry``, the
identifier used in the configuration is the identifier given by the particular
laboratory.  For example, in the case of the `RobotMovement laboratory <https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/experiments/robot_movement/RobotMovementCreatorFactory.java>`_, it defines:

.. code-block:: java

    public class RobotMovementCreatorFactory implements IExperimentCreatorFactory {

        @Override
        public String getCodeName() {
            return "robot-movement";
        }
        
        // ...

So in the ``configuration.js`` the code will be ``robot-movement``.


JavaScript
^^^^^^^^^^
.. note::

    To be written (March 2013).

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

.. _remote_lab_deployment_deploy_experiment_server:

Deploying the Experiment server
-------------------------------
.. note::

    To be written (March 2013).


WebLab-Deusto Python server
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

    To be written (March 2013).

Other servers (XML-RPC based)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

    To be written (March 2013).


Run::

    weblab-admin create foo --xmlrpc-experiment --xmlrpc-experiment-port=10039 --http-server-port=12345

    weblab-admin start foo -m core_machine


.. _remote_lab_deployment_register_in_lab_server:

Registering the experiment server in a Laboratory server
--------------------------------------------------------

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
                    'checkers' : ()
                },
            'exp1:electronics-lesson-2@Electronics experiments' : {
                    'coord_address' : 'electronics2:laboratory1@core_machine',
                    'checkers' : ()
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
                    'checkers' : ()
                },
        }

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

However, you may customize the ``checkers`` that are applied.

.. note::

    Add documentation on checkers and related variables (e.g., "do not check
    this laboratory").

.. _remote_lab_deployment_register_scheduling:

Registering a scheduling system for the experiment
--------------------------------------------------

.. note::

    To be written (March 2013).


.. _remote_lab_deployment_add_to_database:

Add the experiment server to the database
-----------------------------------------

.. note::

    To be written (March 2013).

.. _remote_lab_deployment_grant_permissions:

Grant permissions on this experiment server
-------------------------------------------

.. note::

    To be written (March 2013).


.. _remote_lab_deployment_troubleshooting:

Troubleshooting
---------------

No point defined at this point. In case of errors, :ref:`contact us <contact>`.

Summary
-------

.. note::

    To be written (March 2013).

