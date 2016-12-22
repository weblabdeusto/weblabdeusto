.. _installation_further:

Installation: further steps
===========================

.. contents:: Table of Contents

Introduction
------------

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

Installing external systems
---------------------------

At this point, you have installed the basic requirements. However, now you
should install three new external components:

* **Apache HTTP server:** By default, WebLab-Deusto uses a built-in, simple HTTP
  server written in Python. This web server is not aimed to be used in
  production, but only for demonstration purposes. For this reason, the Apache
  web server (or any other supporting proxies) is recommended.

* **MySQL:** By default, WebLab-Deusto uses SQLite. This configuration suits very
  well low-cost environments (such as Raspberry Pi, where it works). However, in
  desktop computers or servers, this restricts the number of processes running
  the Core Server to one, since SQLite can not be accessed concurrently. Even
  more, it restricts the number of threads to one, so it becomes a bottle neck.
  For few students, this might be fine, but as the number of students increase,
  this becomes an important problem. For this reason, it is better to use other
  database engine. The one used in the University of Deusto for production is
  MySQL.

* **Redis:** There are two main backends for scheduling: one based on SQL (and
  therefore, it can use MySQL or SQLite), and other based on Redis (a NoSQL
  solution that keeps information in memory, becoming very fast). Even in low
  cost devices, the latter is recommended. However, it is only officially
  supported for UNIX. Therefore, if you are running Mac OS X or Linux, install
  Redis and use it as scheduling backend to decrease the time required to
  process users.

GNU/Linux
^^^^^^^^^

All these components are open source and very popular, so they are in most of
the package repositories of each distribution. For example, in Ubuntu GNU/Linux,
you only need to install the following::

   sudo apt-get install apache2 mysql-server redis-server

If you are not using PHP, it is highly recommended to install the ``worker`` MPM
by running::
   sudo apt-get install apache2-mpm-worker
   
.. note::

   For apache on Ubuntu (>16.04) ``apache2-mpm-worker`` is included by default.


This makes that Apache uses threads rather than processes when attending a new
request. This way, the amount of memory required with a high number of
concurrent students is low. However, it is is usually not recommended when also
using PHP, so whenever you install PHP this MPM is usually removed. If you need
to run both, you can use the ``prefork`` MPM, while take into account that it
will require more memory. This is explained in detail in `the official site
<http://httpd.apache.org/docs/2.2/en/mpm.html>`_.

Regarding ``redis``, take into account that redis performs all the operations in
memory **but** from time to time it stores everything in disk, adding latency.
It is recommended to avoid this. In the ``/etc/redis/redis.conf`` file, comment
the following lines::

    save 900 1
    save 300 10
    save 60 10000

By adding a ``#`` before.


Microsoft Windows
^^^^^^^^^^^^^^^^^

In Microsoft Windows, you can install both the Apache HTTP server and MySQL by
using `XAMPP <http://www.apachefriends.org/en/xampp-windows.html>`_. Download it
and install it. XAMPP comes with a control panel to start and stop each service.
In WebLab-Deusto, we are only interested in Apache and MySQL.

Once installed, it is recommended to have the MySQL client in console, so either
do this::

   set PATH=%PATH%;C:\xampp\mysql\bin

Or go to the Microsoft Windows Control Panel -> System -> Advanced ->
Environment variables -> (down) PATH -> edit and append:
``;C:\xampp\mysql\bin``.

If you have problems with XAMPP, check `their FAQ
<http://www.apachefriends.org/en/faq-xampp-windows.html>`_.

Regarding Redis, there is an unofficial version of `Redis for Microsoft Windows
<http://redis.io/download>`_, with a patch developed by Microsoft. However,
while the support is not official or there is an officially supported side
project for supporting Microsoft Windows, we are not recommending its use. So
if you are running Microsoft Windows, simply skip those sections and use MySQL
for scheduling.

Mac OS X
^^^^^^^^

In Mac OS X, Apache is usually installed by default. However, you must install
MySQL by using `the official page <http://www.mysql.com/>`_. You can install
Redis by `downloading it <http://redis.io/download>`_ and compiling it directly.
If you do not manage to run it, remember that it is an optional requirement and
that you can use MySQL as scheduling backend.

.. _native_libraries:

Installing native libraries
---------------------------

By default, the installation process installed a set of requirements, which are
all pure Python. However, certain native libraries make the system work more
efficiently. That said, these libraries require a C compiler to be installed and
a set of external C libraries, which might not be available in Microsoft Windows
environments. However, in GNU/Linux, they are recommended. 

For this reason, in Ubuntu GNU/Linux install the following packages:

.. code-block:: bash

   # Python
   $ sudo apt-get install build-essential python-dev 
   # MySQL client, for an optimized version of the MySQL plug-in
   $ sudo apt-get install libmysqlclient-dev
   # LDAP
   $ sudo apt-get install libldap2-dev 
   # SASL, SSL for supporting LDAP
   $ sudo apt-get install libsasl2-dev libsasl2-dev libssl-dev
   # XML libraries for validating the configuration files
   $ sudo apt-get install libxml2-dev libxslt1-dev 
   # Avoid problems with freetype:
   $ sudo ln -s /usr/include/freetype2 /usr/include/freetype

Once installed, it is now possible to install more optimized Python libraries,
by running:

.. code-block:: bash

   $ cd weblab/server/src/
   $ pip install -r requirements_suggested.txt

From this moment, libraries that improve the performance will be installed.

Scheduling
----------

There are two main database backends for scheduling:

* **SQL based:** using the `SQLAlchemy framework <http://www.sqlalchemy.org/>`_. 
  Two database engines are supported:

  * Using ``SQLite``, which is fast but it requires a single process to be executed,
    so multiple users are managed in a single thread and the latency increases.
  * Using ``MySQL``, which supports multiple students accessing to different
    servers, distributed in several processes or even machines.

* **Redis:** which uses `redis <http://www.redis.io>`_, and provides faster
  results but does only work on UNIX environments at this point.

By default in the introduction section, you have used ``SQLite``. So as to use ``MySQL`` as database engine, run the following:


.. code-block:: bash

   $ weblab-admin create sample --coordination-db-engine=mysql

Additionally, you may pass other arguments to customize the deployment:

.. code-block:: bash

   $ weblab-admin create sample --coordination-db-engine=mysql \
     --coordination-db-name=WebLabScheduling \
     --coordination-db-user=weblab     --coordination-db-passwd=mypassword \
     --coordination-db-host=localhost  --coordination-db-port=3306

However, if you want to use ``Redis``, run the following:

.. code-block:: bash

   $ weblab-admin create sample --coordination-engine=redis

Additionally, you may pass the other arguments, such as:

.. code-block:: bash

   $ weblab-admin create sample --coordination-engine=redis \
     --coordination-redis-db=4  --coordination-redis-passwd=mypassword \
     --coordination-redis-port=6379

So as to change an existing deployment, you may check the variables explained at
:ref:`configuration_variables`, which are located at a file called
``machine_config.py`` in the ``core_machine`` directory.

Database
--------

The WebLab-Deusto database uses `SQLAlchemy <http://www.sqlalchemy.org/>`_,
which is a ORM for Python which supports several types of database engines.
However, in WebLab-Deusto we have only tested two database engines:

* ``SQLite:`` it is fast and comes by default with Python. It suits very well
  low cost environments (such as Raspberry Pi).
* ``MySQL:`` on desktops and servers, it makes more sense to use MySQL and a
  higher number of processes to distribute the load of users among them.

So as to test this, run the following:

.. code-block:: bash

   $ weblab-admin create sample --db-engine=mysql

Additionally, you may customize the deployment with the following arguments:

.. code-block:: bash

   $ weblab-admin create sample --db-engine=mysql  \
     --db-name=MyWebLab     --db-host=localhost    \
     --db-port=3306         --db-user=weblab       \
     --db-passwd=mypassword

You may also change the related variables explained at
:ref:`configuration_variables`, which are located at a file called
``machine_config.py`` in the ``core_machine`` directory.


Summary
-------

With these components installed and validated, now it is possible to enhance the performance in the next section: :ref:`performance`.

