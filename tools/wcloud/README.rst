Summary
~~~~~~~

This system automatically deploys WebLab-Deusto instances, already federated in WebLab-Deusto.
This way, secondary schools or universities may create and administrate their own WebLab-Deusto,
create new users, assign them permissions on certain laboratories, etc.

Architecture
~~~~~~~~~~~~

By running ``start-master-process.sh``, we run the following:

 * We reload the apache server (to guarantee that previous changes have been applied, and which restarts the wCloud server)
 * ``./scripts/admin_worker.sh``, which is a Celery worker running as root. It waits for events in the ``admintasks`` queue and processes them. Typically this is only reloading the apache server.
 * ``./scripts/taskmanager_worker.sh``, which is a Celery worker running as user. It waits for events for creating WebLab-Deusto instances.
 * ``./scripts/starter_worker.sh``, which is a Celery worker running as user. It waits for events for starting WebLab-Deusto instances.
 * ``wcloud/weblab_starter.py``, which populates the starter queue with the existing instances.

Deployment
~~~~~~~~~~

Then, configure the settings.py script with the database credentials. Deploy the database::
  
  python deploy.py

Create all the MySQL databases to have a pool of databases (1000 in this case)::

  python db_creator.py -p wcloud -e 1000 -u weblab -pw

Now you can run wcloud. It takes 4 steps:

* Running the web server. For debugging you may use the following command. For production, refer to the `flask documentation <http://flask.pocoo.org/docs/deploying/>`_::

  python run.py # IMPORTANT: Only in debugging mode.

* Running the Task Manager::

  python wcloud/taskmanager.py

* Running the WebLab-Deusto starter process::

  python wcloud/weblab_starter.py

* Running the Apache Reloader as root::

  sudo python apache_reloader.py

The web server can be run with the permissions of a typical web server user (e.g. nobody or www-data), while the Task Manager and the WebLab-Deusto starter processes should be run as a regular user running WebLab-Deusto. Finally the apache reloader process must be run as root.

TODO list
~~~~~~~~~

* Make the system transactional (in the except: remove the apache config, etc.)

* Automatically register a user in WebLab-Deusto.
* Establish default permissions
* Remove the Launcher of raw_input

* setup.py
* Find out why unicode with utf-8 is failing



UNIT TESTING
~~~~~~~~~~~~

The system is being redesigned to be somewhat generic. However, the Unit Testing still makes some assumptions.
Those are the following:

* A MySQL server is running.
* The root MySQL user is "root" and its password is: "password".




ACKNOWLEDGEMENTS
~~~~~~~~~~~~~~~~

.. image:: logos/mcloud.png
  :alt: mCloud project
  :align: center

wCloud is part of the `mCloud project <http://innovation.logica.com.es/web/mcloud/>`_ (IPT-2011-1558-430000), 
Este proyecto ha recibido financiación del Ministerio de Economía y Competitividad, dentro del Plan Nacional 
de Investigación Científica, Desarrollo e Innovación Tecnológica 2008-2011 y el Fondo Europeo de Desarrollo Regional (FEDER).

.. image:: logos/feder.png
  :alt: FEDER: Una manera de hacer Europa
  
.. image:: logos/inn.jpg
  :alt: Innpacto
  
.. image:: logos/mec.png
  :alt: Ministerio de Economía y Competitividad


