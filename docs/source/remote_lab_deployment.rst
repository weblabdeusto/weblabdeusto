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
source code `here
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
.. note::

    To be written (March 2013).

Flash
^^^^^
.. note::

    To be written (March 2013).


.. _remote_lab_deployment_deploy_experiment_server:

Deploying the Experiment server
-------------------------------
.. note::

    To be written (March 2013).


Introduction
^^^^^^^^^^^^
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

.. note::

    To be written (March 2013).

    This covers the changes on the core and the laboratory server, as well as
    the database.

.. _remote_lab_deployment_register_scheduling:

Registering a scheduling system for the experiment
--------------------------------------------------

.. note::

    To be written (March 2013).

    This covers the changes on the core and the laboratory server, as well as
    the database.


.. _remote_lab_deployment_add_to_database:

Add the experiment server to the database
-----------------------------------------

.. note::

    To be written (March 2013).

    This covers the changes on the core and the laboratory server, as well as
    the database.

.. _remote_lab_deployment_grant_permissions:

Grant permissions on this experiment server
-------------------------------------------

.. note::

    To be written (March 2013).

    This covers the changes on the core and the laboratory server, as well as
    the database.



.. _remote_lab_deployment_troubleshooting:

Troubleshooting
---------------

No point defined at this point. In case of errors, :ref:`contact us <contact>`.

Summary
-------

.. note::

    To be written (March 2013).

