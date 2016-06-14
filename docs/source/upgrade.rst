.. _upgrade:

Upgrading
=========

You have installed WebLab-Deusto. However, you notice that there is a super-cool
feature in a newer version. And you want to upgrade your current setup to this version.

There are several things that may change from one version to other:

#. The client code
#. The server code
#. Some new or old parameters changed
#. The database schema

The first two points only require you to download the changes and re-deploy it.
The other two will require you to also modify your WebLab instance. We provide
tools for all this.

.. contents:: Table of Contents

Upgrading the base system
-------------------------

So as to download the latest version, download the latest changes from the git
repository. Basically, go to the directory where WebLab-Deusto is and do the
following::

 # Go wherever you downloaded it
 $ cd /opt/weblabdeusto/
 $ git pull

Then, the code changes will be there, but they will still not be deployed.  Now you need to deploy both the code, by running::

 # Go wherever you downloaded it
 $ cd /opt/weblabdeusto/
 $ python setup.py install

.. warning::

    Before running the ``setup.py install`` process, you may need to delete the directory
    called ``build`` in the ``server/src`` directory. The reason is that sometimes, some
    old files are left there. Most of the times this step is not mandatory, but from time
    to time, it is required.

This will install all the new requirements, will copy everything to the deployment directory. From this point, you may create new WebLab-Deusto instances using the new deployment, by running::

 $ weblab-admin create sample

As already explained in :ref:`first_steps`.

Upgrading an existing instance
-------------------------------

If you already have a running WebLab-Deusto instance, then you may want to
upgrade it. This means changing the structure of the database, configuration
variables and so on.

WebLab-Deusto, through its ``weblab-admin`` command, manages this, modifying
the database and converting the old variables. However, this command may fail
(there are too many combinations), and if it fails, your system might end up in
an unrecoverable state. For this reason, you are encouraged to make a backup of
both the WebLab-Deusto instance directory and the database (if it is SQLite,
it's inside the directory, but if it is MySQL, it is outside it, and you might
need a command like `mysqldump
<http://dev.mysql.com/doc/refman/5.5/en/mysqldump.html>`_).

.. warning::

    You are encouraged to make backups of your data before proceeding, and even
    to run the following command in a copy of the directory using a different
    database.

So as to use the automatic upgrader, first stop your current instance, and then
run the following::

 $ weblab-admin upgrade sample

If you have made further changes (such as the location of the virtualenv, or the directory where the deployment is), you need to reconfigure the paths, by running the following and restart the web server (e.g., Apache)::

 $ weblab-admin httpd-config-generate sample

Once finished, you will be able to start again your system::

 $ weblab-admin start sample

If there is any error, please :ref:`report it <contact>`.
