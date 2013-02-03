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

Now you can run wcloud. It takes 4 steps:

* Running the web server. For debugging you may use the following command. For production, refer to the `flask documentation <http://flask.pocoo.org/docs/deploying/>`_::

  python runserver.py # IMPORTANT: Only in debugging mode.

* Running the Task Manager::

  python wcloud/taskmanager.py

* Running the Apache Reloader as root::

  sudo python apache_reloader.py

* Running the WebLab-Deusto starter process::

  python wcloud/weblab_starter.py

TODO list
~~~~~~~~~

* Force a base URL (e.g. /w/). Started, but some errors were found.
* Make the system transactional (in the except: remove the apache config, etc.)

* Automatically register a user in WebLab-Deusto.
* Establish default permissions
* Remove the Launcher of raw_input

* setup.py
* Find out why unicode with utf-8 is failing

