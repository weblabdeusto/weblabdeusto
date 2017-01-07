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

Secure the deployment
---------------------

This section covers few minimum steps to secure your WebLab-Deusto deployment.

Secure the communications
^^^^^^^^^^^^^^^^^^^^^^^^^

WebLab-Deusto supports HTTPS, and it is designed so that it can easily work with
it (e.g., in the managed approach, all the connections go through the core
server). **We highly recommend you to install SSL certificates** to reduce the risk
of potential attacks to your WebLab-Deusto deployment, especially if you or your
students submit the credentials through WebLab-Deusto (as it happens when using
database passwords or LDAP).

.. note::
  **A note about SSL**

  In case you are unfamiliar with HTTPS (HTTP Secure or HTTP over SSL), all the
  web uses the HTTP protocol (**http://**). However, this protocol goes
  unencrypted, so anyone in the middle (people in the same WiFi, ISPs, layers in
  the middle between the final client and the server...) can read the traffic.
  For this reason, HTTPS (**https://**) was developed, which supports HTTP
  through an SSL connection, which encrypts the communications. Nowadays there
  is a big effort to make as much of the web use HTTPS (e.g., not only
  e-commerce sites but also google.com, Wikipedia, Facebook and even this
  website where you are reading this... all go through HTTPS).
  
  You can generate SSL certificates by yourself (and signed by yourself).
  However, in general web browsers will not accept them (or they will show a
  big warning before accessing), because otherwise you could create an SSL
  certificate for another website that you do not own, and they would not be
  able to know. This could lead to different types of attacks. 
  
  For this reason, web browsers come with a set of CA (Certificate Authorities),
  and they only trust whatever is signed by them (or signed by whoever they
  delegate). Additionally, they have other complex mechanisms (such as lists of
  revoked certificates, etc.).

  So, when you install a valid certificate, some CA (or delegated) will verify
  that you are the valid owner of a server, and it will create and sign a
  certificate for you. When users access your website using **https://** to your
  host, when starting the connection they will automatically download the public
  key (which they will use for encrypting) and the signature of this key
  provided by a CA. They will validate with the installed CA if this key is
  valid for this particular domain (e.g., ``weblab.yourinstitution.edu``, and if
  it is, it will proceed to encrypt the connection). Otherwise (e.g., the key is
  expired, the CA does not recognize the signature, the server name is different
  -www.weblab.yourinstitution.edu instead of weblab.yourinstitution.edu-, the
  key is in a revocation list), it will show an error instead.
  
  As a final note, one certificate can server multiple domain names for a
  particular server. For example, you might have a certificate for
  ``*.weblab.yourinstitution.edu`` and you can use it in different servers
  (e.g., ``cams.weblab.yourinstitution.edu``,
  ``www.weblab.yourinstiution.edu``...). Those are called *wildcard
  certificates* (and if you choose to request those, take into account that
  ``*.weblab.yourinstitution.edu`` is not valid for
  ``weblab.yourinstitution.edu`` so in addition you'll need an alternate name).
  You may also select different names, listed in what is called the *Alternate
  names* (manually providing a list, such as ``weblab.yourinstitution.edu`` and
  ``www.weblab.yourinstitution.edu`` and ``cams.yourinstitution.edu``, etc.).

So, once you have installed WebLab-Deusto in your **final server** (i.e., with a
proper hostname such as ``weblab.yourinstitution.edu``), you might want to
install the SSL certificates. To do so, there are three approaches:

* ``Contact your IT services:`` many institutions (e.g., universities, research
  centers) already have agreements to create free SSL certificates. You should
  first contact to your IT services to see if they provide you this service.
* ``Buy a SSL certificate:`` there are many websites where SSL certificates are
  sold and managed, with different options of security.
* ``Get a free SSL certificate by Let's Encrypt:`` `Let's Encrypt
  <https://letsencrypt.org/>`_ is an open initiative to secure the Internet that
  provides free SSL certificates in an automatic basis. The certificates only
  last a couple of months, but you can renew them automatically. All what you
  need is having your server already configured with the **final** IP address
  and hostname (so they automatically verify that ``weblab.yourinstitution.edu``
  is indeed your server), and running already a proper web server (e.g., Apache
  or nginx). For more information on how to do it (it literally takes a couple
  of minutes), go to the `Certbot <https://certbot.eff.org/>`_ site created by
  the `EFF (Electronic Frontier Foundation) <https://www.eff.org/>`_. It tells
  you what software to install and how. ``Let's Encrypt`` does not support
  wildcard certificates, but it supports as many alternate names as you want.

Once you install the certificate in your Apache server (each provider will
explain you how), you should go to the ``core_host_config.py`` file and change
the ``core_server_url`` variable to your final URL (e.g.,
``https://weblab.yourinstitution.edu/weblab/``).

Additionally, in Apache there is a directive that you might want to use in the
``VirtualHost`` using the 80 port such as::

  RedirectMatch ^/weblab/(.*)$ https://weblab.yourinstitution.edu/weblab/$1

So that everything that arrives to the 80 port (**http://**) is forwarded to the 
443 port (**https://**).

Close access to local services
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The internet is a quite dangerous place, where there are robots constantly
checking random IPs and searching for open services to attack (such as
databases, shared directories, cameras, printers...). In your WebLab-Deusto
server, you probably don't want anything open other than the WebLab-Deusto
server (and other services that you in purpose want open). There are two ways to
do this, and we recommend both:

* First, install a proper firewall. You might use the one provided by your
  Operating System (such as the Windows Firewall in Microsoft Windows, or
  iptables in Linux). Make it possible to access only those services that you
  need open. WebLab-Deusto itself does not require any port open (only those for
  the web browser, which are 80 and 443).
* Second, review your services. In particular, make sure that both Redis and
  MySQL are bound to 127.0.0.1 (instead of open to the whole Internet). This is
  usually established in its configuration files (e.g., search for a parameter
  called ``bind-address`` in MySQL or ``bind`` in redis. It may be called
  ``listen`` in other services).

After doing it, or in case of doubt, check from outside (e.g., your home)
connecting to those ports::

   (3306 is the default MySQL port)
   $ telnet weblab.myinstitution.edu 3306
   Trying 1.2.3.4...
   telnet: Unable to connect to remote host: Connection timed out
   $
   
   (6379 is the default Redis port)
   $ telnet weblab.myinstitution.edu 6379
   Trying 1.2.3.4...
   telnet: Unable to connect to remote host: Connection timed out
   $

If the response is something like::

   telnet: Unable to connect to remote host: Connection refused

it's also fine. However, if it ever says::

   $ telnet weblab.myinstitution.edu 
   Trying 1.2.3.4...
   Connected to weblab.myinstitution.edu.
   Escape character is '^]'.

It means that those ports are open and can be accessed by attackers. By default,
some services (as MySQL) require credentials, but sometimes there is a
vulnerability in the software and external attackers can access more than they
should. Also, if you are using easy passwords (e.g., the ones in the
documentation), the risk of attack increases if the services are open to the
Internet.

For those services that you also want to make available but only for you (and
not for the general audience), you should also change the default ports. For
example, if you use Remote Desktop, VNC or SSH, you can use it in a different
port than the default one. For example, SSH is a secure service, but it has had
important vulnerability problems in the past. And for those robots that are
constantly checking for services open, they might be looking in each IP address
for a SSH service running in the 22 port (the default one). If you have it in
the 16483 one, it might be more difficult for them to find it and attack it,
unless they're indeed targeting your server. As an additional measure, there are
approaches such as `port-knocking
<https://en.wikipedia.org/wiki/Port_knocking>`_ which let you define a set of
random ports (e.g., 5356, 15243 and 9513), and when you *knock* them (e.g.,
trying to connect to them) in that order, suddenly the firewall opens access to
these services (e.g., SSH). This way, even if someone checks all the ports open
in your server, they will only find the public ones (e.g., Apache), and only if
they connect to different ports in an order they will see that service available.

Upgrade your software frequently
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All software is inherently subject to have vulnerabilities. Once they are
discovered and fixed, when you upgrade them, the vulnerabilities are not there
anymore. However, if you upgrade once a month, then you might run into troubles
for that month.

This does not mean that you need to use the latest Ubuntu distribution. For
example, if you are using a Ubuntu Server 12.04 LTS, it will be supported until
June 2017. You are of course encouraged to use Ubuntu 16.04 LTS (the latest
LTS), but it is not really a priority. What is important is to use an Operating
System version that is still supported (and for this reason, in the case of
Ubuntu, it is better to install LTS versions -that are supported for longer:
e.g., 14.04, 16.04- than not LTS versions -e.g., 16.10-) and upgrade it every
day (you can install a script for that). If you are using software not managed
by your operating system (e.g., Apache on Windows), you should also upgrade it
frequently (and you can join for example their `mailing lists
<http://httpd.apache.org/lists.html#http-announce>`_ to be notified of new
versions). This is not required in systems as Linux, where most of the software
required by WebLab-Deusto is installed from the repositories. However, you still
have to make sure that it is upgraded frequently.

It is also important to :ref:`upgrade the WebLab-Deusto <upgrade>` regularly
(not so often as every day, but keep it in mind). It's not only about
WebLab-Deusto itself, but about the libraries used by WebLab-Deusto (which are
automatically upgraded when you upgrade WebLab-Deusto). Usually in the main
screen of WebLab-Deusto you have a link to GitHub (where it says ``version
r<number>``). If you click that link and compare it with `this one
<https://github.com/weblabdeusto/weblabdeusto/commits/master>`_, you can see if
there were new versions since you last upgraded it. You may also use the
:ref:`WebLab-Deusto mailing list <contact>` to receive notifications on
potential issues.

Deployment
----------

.. note::

   This section is only for deployments in UNIX environments. In Windows
   environments you can use services by wrapping WebLab into ``.bat`` files.

WebLab-Deusto can be run as a script, but you might want to deploy it as a
service. However, given that it is very recommendable **not** to install it as
root (unless you play with virtuaelnvs to avoid corrupting the system with wrong
versions of the libraries), it is better to install it in a system such as
`supervisor <http://supervisord.org/>`_. In supervisor you can add any type of
program and they will run as services. You also have a tool to control which
services are started, or restart them when required (e.g., when upgrading or
modifying the ``.py`` or ``.yml`` files).

This section is focused on how to install this tool in a UNIX (e.g., Linux)
environment.

Step 1: installation of supervisor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on your Operating System, you might find it in the OS packages itself.
For example, in Ubuntu run::

  $ sudo apt-get install supervisor

And you're done. Otherwise go to `supervisor docs on installation
<http://supervisord.org/installing.html>`_ for futher information.

Once installed, you'll see that you can start supervisor and check the status::

  $ sudo service supervisor start
  $ sudo supervisorctl help

  default commands (type help <topic>):
  =====================================
  add    exit      open  reload  restart   start   tail   
  avail  fg        pid   remove  shutdown  status  update 
  clear  maintail  quit  reread  signal    stop    version

  $ sudo supervisorctl status
  $ 

It is normal that status returns nothing since we have not installed any service
yet.

Step 2: prepare WebLab for being used as a service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's imagine that you have installed WebLab-Deusto using ``virtualenvwrapper``
and called it ``weblab``. Then, the virtualenv will typically be located in
something like::

   /home/tom/.virtualenvs/weblab/

And the activation script will be in::

   /home/tom/.virtualenvs/weblab/bin/activate

And let's imagine that you have created a new WebLab-Deusto instance in your
home directory, in a ``deployments`` directory and called it ``example``, such
as::

   $ cd /home/tom/deployments/
   $ weblab-admin create example --http-server-port=12345

Then, we will create a wrapper file in any folder (e.g., in the ``deployments``) directory called for example ``weblab-wrapper.sh`` which will contain the following three lines:

.. code-block:: bash

   #!/bin/bash
   _term() {
      kill -TERM "$child" 2>/dev/null
   }

   # When SIGTERM is sent, send it to weblab-admin
   trap _term SIGTERM

   source /home/tom/.virtualenvs/weblab/bin/activate
   weblab-admin $@ &
   
   child=$!
   wait "$child"

And then we will grant execution privileges to that file::

    $ chmod +x /home/tom/deployments/weblab-wrapper.sh

From this point, calling it from anywhere will use the virtualenv will work::

    $ cd /tmp/
    $ /home/tom/deployments/weblab-wrapper.sh
    Usage: /home/tom/.virtualenvs/weblab/bin/weblab-admin option DIR [option arguments]

        create                  Create a new weblab instance
        start                   Start an existing weblab instance
        stop                    Stop an existing weblab instance
        monitor                 Monitor the current use of a weblab
        instance
        upgrade                 Upgrade the current setting
        locations               Manage the locations
        database
        httpd-config-generate   Generate the HTTPd
        config files (apache, simple, etc.)

    $ 

Step 3: Create the configuration for supervisor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now what you have to do is to create a file such as ``example.conf`` (it is
important that it ends by ``.conf``) for running the example instance as a
service. To do so, create a file such as the following::

    [program:example]
    command=/home/tom/deployments/weblab-wrapper.sh start example
    directory=/home/tom/deployments/
    user=tom
    stdout_logfile=/home/tom/deployments/example/logs/stdout.log
    stderr_logfile=/home/tom/deployments/example/logs/stderr.log
    killasgroup=true

There are plenty more of configuration variables in supervisor (such as not
exceeding the stdout/stderr logs in more than a number of MB, moving them until
you have more than 10 files, etc.): check the documentation at the `supervisor
[program:x] section documentation
<http://supervisord.org/configuration.html#program-x-section-values>`_.

Step 4: Add the configuration to supervisor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Then, you have to add this file to supervisor. In Ubuntu Linux this is typically
done by copying the file to ``/etc/supervisor/conf.d/`` and then using the
``supervisorctl`` to add it::

    $ sudo cp example.conf /etc/supervisor/conf.d/
    $ sudo supervisorctl update
    example: added process group
    $ 

At this point, you might check that your WebLab-Deusto instance is running. By
default when you update the supervisorctl, it runs the process. First check in::

    $ sudo supervisorctl status
    example                          RUNNING   pid 12428, uptime 0:00:04
    $ 

And then go with your web browser to see if it is running (in the example
created, you can go to ``http://localhost:12345/``, but you should be using
Apache as described above).

Step 5: Try supervisor
^^^^^^^^^^^^^^^^^^^^^^

Once configured, it becomes easier to start the cycle of the deployment. For example::

   $ sudo supervisorctl start example
   example: started
   $ sudo supervisorctl status example
   example                          RUNNING   pid 19320, uptime 0:00:18
   $ sudo supervisorctl stop example
   example: stopped


Summary
-------

With these components installed and validated, now it is possible to enhance the performance in the next section: :ref:`performance`.

