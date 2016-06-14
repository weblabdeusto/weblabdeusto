.. _performance:

Performance
===========

.. contents:: Table of Contents

Introduction
------------

This section focuses on explaining how to increase the performance of the system
by customizing it with the proper arguments. You may use the WebLab Bot
(:ref:`bot`) to see what parameters work best in your environment.

Core servers
------------

Python has a `Global Interpreter Lock (GIL)
<http://en.wikipedia.org/wiki/Global_Interpreter_Lock>`_ that makes the
threading model not work as could be expected when coming from other programming
languages. Internally in Python, when a thread is being run, it executes a
number of instructions which can be configured and then it swaps the context and
other thread is executed. Whenever there is an IO (input/output) operation, or
some extension developed in C is called, the context will also be swapped. The
problem is that during the execution of the pure Python not-IO operations, the
GIL is locked, so no other operation can be executed in other processor.

Given the amount of IO in WebLab-Deusto (IO includes not only the requests from
the client and the requests to the particular laboratory, but also the database
and all the access to the Redis server), certain concurrence will often occur
even with a single process. However, in order to take advantage of the nowadays
common dual, quad or more core processors, it can be managed using multiple
copies of Python processes instead of relying on the Python threading model.

For this reason, WebLab-Deusto has been designed so it can scale and multiple
independent processes can be executed not only in different machines, but also
in the same machine to mitigate this effect. This way, having 4 processes
running WebLab-Deusto in a quad core machine will increase the throughput.

In the following drawing, the WebLab Bot (see :ref:`bot`), which is a
student simulator that tests different loads of highly concurrent users (i.e.
users clicking on the *Reserve* button at the very same time), measures times
using different numbers of processes (1 and 5) with different database backends
(MySQLdb and PyMySQL). This shows the reservation method:


.. figure:: /_static/multiple_cores.png
   :width: 600 px
   :align: center

   The red line represents the maximum value, the blue line the minimum value,
   and the green line the mean and the standard deviation. Each measurement (e.g.,
   140 students with the MySQL db) have been taken 5 times.


As it is shown, when using a single process (``1 core``), MySQL performs better
once you increase the number of concurrent students. There are two Python
libraries for using MySQL, one in pure Python (PyMySQL), and a native one, which
requires you compiling the code as explained in the section
:ref:`native_libraries`. The native one works faster than the pure Python
version.

However, the biggest change is when you increase the number of processes (e.g.,
``5 core servers``). This is something you can not do if you are using SQLite,
but yes with MySQL. For this reason, you will get an error when you run::

    $ weblab-admin create sample --cores 4
    ERROR: sqlite engine selected for coordination, general database is
    incompatible with multiple cores

The way to create a new WebLab-Deusto deployment with 4 core servers and using
MySQL for both database and scheduling is::

    $ weblab-admin create sample --cores 4 --coordination-db-engine=mysql --db-engine=mysql

This generates a WebLab-Deusto system with 4 Core servers and 4 Login servers.
Apache will balance the load of users among them, so each of these process will
only process a subset of the users.

Scheduling backends
-------------------

So as to store information (permissions, uses, students, etc.), WebLab-Deusto
uses a relational database (MySQL or SQLite). However, for managing the
scheduling (who's first), it may use a relational database (again, MySQL or
SQLite) or the `Redis <http://redis.io/>`_ NoSQL system. This backend also
supports load balancing (and therefore, multiple core servers), but since all
the information is managed in memory, it is much faster.

Indeed, in the following figure the MySQLdb library with MySQL is compared with
Redis, with 1 and 5 core servers. As it can be seen in the drawing, Redis is
considerably faster. In older machines, this difference is even multiplied.

.. figure:: /_static/redis_vs_mysql.png
   :width: 600 px
   :align: center

   The red line represents the maximum value, the blue line the minimum value,
   and the green line the mean and the standard deviation. Each measurement (e.g.,
   140 students with the MySQL db) have been taken 5 times.

For this reason, using Redis is recommended. However, Redis is not officially
supported on Microsoft Windows at this moment.

Apache
------

You should use a robust HTTP server instead of the one that comes by default
when you pass the following option::

   $ weblab-admin create sample --http-server-port=12345

At this moment, WebLab-Deusto generates the configuration for the Apache HTTP
server, so you might use it. Support for autogenerating the configuration of
other servers might be added soon. When you create the deployment, the message
shown explains what you need to add in which files. For example, in GNU/Linux,
at the time of this writing, it details the following::

    $ weblab-admin create sample

    Congratulations!
    WebLab-Deusto system created

    Append the following to a new file that you must create called /etc/apache/conf.d/weblab

        Include "/tmp/sample/httpd/apache_weblab_generic.conf"

    And enable the modules proxy proxy_balancer proxy_http headers.
    For instance, in Ubuntu you can run: 

        $ sudo a2enmod proxy proxy_balancer proxy_http headers

    Then restart apache. If you don't have apache don't worry, delete sample and 
    run the creation script again but passing --http-server-port=8000 (or any free port).

This message is different in each operating system, and it takes into account
what files it finds.

Additionally, as previously explained, Apache has different `MPMs
<http://httpd.apache.org/docs/2.2/en/mpm.html>`_. In GNU/Linux, when PHP is
installed, Apache typically uses the ``prefork`` MPM. The ``worker`` MPM
consumes much less memory, so it is recommended. However, if you need to support
PHP or you are working in other operating systems, you may use the existing MPM,
although you should measure how much memory is Apache consuming.

Raspberry Pi and low cost devices
---------------------------------

WebLab-Deusto is a very light system, which does not require much memory.
Indeed, we have successfully deployed the whole system even in Raspberry Pi
devices, and measured the results. As you can see in the following drawing, this
ARM device, with only 256 MB RAM, could manage different amounts of users, while
the amount of time increased fastly. It was using SQLite as database, everything
(Experiment Server, Core Server, Laboratory Server and Login Server) in a single
process, and ``Redis`` (left) and ``SQLite`` (right) for scheduling.

.. figure:: /_static/raspberry_results.png
   :width: 600 px
   :align: center

   The red line represents the maximum value, the blue line the minimum value,
   and the green line the mean and the standard deviation. Each measurement (e.g.,
   140 students with the MySQL db) have been taken 5 times. Note that each row
   has a different scale.

As it can be seen there, even in a Raspberry Pi device, ``Redis`` is more
suitable. However, in such a cheap device (around $ 35) the system becomes
substantially slower. The typical deployment is having a set of regular servers
for the main services (Core Server and Login Server), and multiple raspberries
for the different experiments.

Summary
-------

In this section, more complex deployments have been addressed. It uses extensively the ``weblab-admin`` script, and therefore, it does not explain how this is managed internally. So as to understand the files generated by this script, continue with the next section, :ref:`directory_hierarchy`.

