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

  python db_creator.py -p wcloud -e 1000 -u weblab -pw

Now you can run wcloud. It takes 3 steps:

* Running the web server. For debugging you may use the following command. For production, refer to the `flask documentation <http://flask.pocoo.org/docs/deploying/>`_::

  python runserver.py # IMPORTANT: Only in debugging mode.

* Running the Task Manager::

  python wcloud/taskmanager.py

* Running the Apache Reloader as root::

  sudo python apache_reloader.py


TODO list
~~~~~~~~~

* Script to start all the WebLab-Deusto instances at the beginning
* Reload status page automatically
* Load the admin page in the generated WebLab-Deusto (and not www.weblab.deusto.es)
* Disable re-deploying or changing configuration once a deployment has been established.
* Show a link to the final working system.
* Don't show the status
* Find out why unicode with utf-8 is failing

* Have a Home in the "configure"

* Front page should show more documentation
* About, Contact, etc. does not show anything
* setup.py

