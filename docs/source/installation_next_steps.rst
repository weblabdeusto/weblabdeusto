.. note::

   **THIS SECTION IS BEING WRITTEN (MARCH 2013)**

.. _installation_further:

Installation: further steps
===========================

.. contents:: Table of Contents

Introduction
~~~~~~~~~~~~

As previously detailed, right now you should have the simplest WebLab-Deusto up
and running. It uses SQLite as main database (so only one process can be running) 
and SQLite as scheduling mechanism (which is very slow). Additionally, you have all the
servers in a single process, so you can not spread the system in different
machines. Finally, you are not using a real HTTP server, but the one built-in,
which is very slow and not designed for being used in production. These settings
in general are highly not recommended for a production environment.

In this section we will focus on installing and validating the installation of
more components, as well as playing with simple deployments which use these
installations. With these components, it is possible to enhance the performance
in the next section: :ref:`performance`.

More requirements
~~~~~~~~~~~~~~~~~

.. note::

   **TO BE WRITTEN**

At this point, you have installed the basic requirements. However, now you
should install three new components:

* Apache HTTP server: it will .
* MySQL
* Redis

Apache
``````

MySQL
`````

Redis (optional)
````````````````

Scheduling
~~~~~~~~~~

.. note::

   **TO BE WRITTEN**


Database
~~~~~~~~

.. note::

   **TO BE WRITTEN**


LDAP
~~~~

.. note::

   **TO BE WRITTEN**


Summary
~~~~~~~

With these components installed and validated, now it is possible to enhance the performance in the next section: :ref:`performance`.


.. toctree::
   :maxdepth: 2

   deploying_vm_experiment
