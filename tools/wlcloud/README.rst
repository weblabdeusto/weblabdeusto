Summary
~~~~~~~

This system automatically deploys WebLab-Deusto instances, already federated in WebLab-Deusto.
This way, secondary schools or universities may create and administrate their own WebLab-Deusto,
create new users, assign them permissions on certain laboratories, etc.

Deployment
~~~~~~~~~~

Install the requirements::

  pip install -r requirements.txt

Then, configure the settings.py script with the database credentials. Deploy the database::
  
  python deploy.py

Create all the MySQL databases to have a pool of databases (1000 in this case)::

  python db_creator.py -p wlcloud -e 1000 -u weblab -pw

Now you can run wlcloud. It takes 3 steps:

* Running the web server. For debugging you may use the following command. For production, refer to the `flask documentation <http://flask.pocoo.org/docs/deploying/>`_::

  python runserver.py # IMPORTANT: Only in debugging mode.

* Running the Task Manager::

  python wlcloud/taskmanager.py

* Running the Apache Reloader as root::

  sudo python apache_reloader.py


TODO list
~~~~~~~~~

* Front page does not show a link to /configure
* Front page should show more documentation
* About, Contact, etc. does not work
* setup.py
* General script that is installed with setup.py which runs the taskmanager, the apachereloader and the MySQL creation

