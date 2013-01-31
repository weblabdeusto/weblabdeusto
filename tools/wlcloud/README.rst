Summary
~~~~~~~

This system automatically deploys WebLab-Deusto instances, already federated in WebLab-Deusto.

Deployment
~~~~~~~~~~

Install the requirements::

  pip install -r requirements.txt

First, configure the settings.py script with the database credentials. Then, deploy the database::
  
  python deploy.py

Create all the MySQL databases (script missing)::

  python db_creator.py

Now you can run wlcloud. It takes 3 steps:

* Running the web server::

  python runserver.py # In debugging mode

  ./run.sh # In production mode (check the flask WSGI documentation)

* Running the Task Manager::

  python wlcloud/taskmanager.py

* Running the Apache Reloader as root::

  python apachereloader.py


TODO list
~~~~~~~~~

* Front page does not show a link to /configure
* Front page should show more documentation
* About, Contact, etc. does not work
* MySQL initial database creation (a script is required)
* setup.py
* General script that is installed with setup.py which runs the taskmanager, the apachereloader and the MySQL creation
* When you call deploy, it does not show any message

