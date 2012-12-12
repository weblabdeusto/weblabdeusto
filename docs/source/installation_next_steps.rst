.. _toctree-directive:
.. _installation_further:

Installation: further steps
===========================

As previously detailed, right now you should have the simplest WebLab-Deusto up
and running. It uses sqlite as main database (so only one process can be running) 
and sqlite as scheduling mechanism (which is slow). Additionally, you have all the
servers in a single process, so you can not spread the system in different machines.
These settings in general are highly not recommended for a production environment.
In this section we will focus on more complex deployments, using redis for scheduling,
MySQL as database, supporting LDAP, etc.

**THIS SECTION HAS NOT BEEN WRITTEN YET**

(anyway, if you're an advanced user and running a UNIX system -Mac OS X included-, just run::

   pip install -r requirements_suggested.txt

and later take a look at options weblab-admin.py --help)

.. toctree::
   :maxdepth: 2

   deploying_vm_experiment
