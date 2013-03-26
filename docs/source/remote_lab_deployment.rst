.. _remote_lab_deployment:

Remote laboratory deployment
============================

.. contents:: Table of Contents

Introduction
------------

In the :ref:`previous section <remote_lab_development>` we have covered how to
create new remote laboratories using the WebLab-Deusto APIs. However, we have
not covered how to use them in an existing deployment of WebLab-Deusto. This
section covers this task. This way, here we will see how to register the
already developed clients and servers.

There are three major steps:

#. Deploy the experiment client
#. Deploy the experiment server
#. Register the experiment

Deploying the Experiment client
-------------------------------
.. note::

    To be written (March 2013).

Introduction
^^^^^^^^^^^^
.. note::

    To be written (March 2013).

Google Web Toolkit
^^^^^^^^^^^^^^^^^^
.. note::

    To be written (March 2013).


JavaScript
^^^^^^^^^^^^^^^^^^
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


Registering the Experiment
--------------------------

.. note::

    To be written (March 2013).

    This covers the changes on the core and the laboratory server, as well as
    the database.

Summary
-------

.. note::

    To be written (March 2013).

