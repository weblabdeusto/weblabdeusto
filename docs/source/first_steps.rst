.. _first_steps:

First steps
===========


In this section, we will learn to create our first deployment of a WebLab-Deusto
instance. This section assumes that you have successfully :ref:`installed the
system <installation>`. It also assumes that you have activated the proper
virtual environment in the current terminal, so running weblab-admin works::

  $ weblab-admin.py --version
  5.0

The deployment we are running here is very small and relies of very few
technologies. It has successfully been deployed even in `Raspberry Pi
<http://www.raspberrypi.org/>`_ devices. But it also has several drawbacks:
performance, lack of concurrent support for certain operations, etc. We will see
how to implement more complex scenarios in `other section
<installation_further>`, but for bootstrapping a WebLab-Deusto instance and
learning the basic concepts, this is enough.

Creating a WebLab-Deusto instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A single computer may have multiple instances of WebLab-Deusto. In production,
there will be typically a single one, but for testing it may be useful to play
with different ones. Each instance will manage its own permissions, its own
users, its own queues, etc.

So as to create a new WebLab-Deusto instance, run the following::

  $ weblab-admin.py create example --http-server-port=8000
  Congratulations!
  WebLab-Deusto system created
  [...]
  Enjoy!

  $ 

From this point, in that directory (*example*), a full WebLab-Deusto deployment
will be established. If you take a look inside, you will see different
directories (for databases -*db*-, web servers -*httpd*-, logs -*logs*,
*files_stored*-), and there will be one which contains all the deployment
configuration, called *core_machine*. Inside it, you will see a hierarchy of
directories with configuration files that apply to each server. 

Starting the WebLab-Deusto instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The WebLab-Deusto instance at this point is configured, but it is not started.
So as to start it, we will use once again the *weblab-admin.py* command. As you'll
find out, this is the command that you will use for any management related with
the instances. Run the following::

  $ weblab-admin.py start example
  Press <enter> or send a sigterm or a sigint to finish

As you can see, the server is running. By pressing enter, the server will stop::

  (enter)
  Stopping servers...
  $

So, let's start it again::

  $ weblab-admin.py start example
  Press <enter> or send a sigterm or a sigint to finish


And, while it is started, let's use it for the very first time. Open in your web
browser the following address: http://localhost:8000/ 

You will find the log in screen of WebLab-Deusto. On it, log in using *admin* as
username and *password* as password. You will see that there are some sample
laboratories. One of them (*dummy*) is local, and it does not rely on any
hardware equipment. The rest are demo laboratories located in the University of
Deusto. By default, these laboratories are created and assigned to the
administrators group. They use the federation model of WebLab-Deusto to connect
to WebLab-Deusto and use real equipment there.

You can safely play with both types of laboratories. With the dummy laboratory,
you will see several output lines in the terminal from which you run
WebLab-Deusto.

Managing users and permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ok, so everything is working for the *admin* user. What about creating a class
of 20 students who can access only the dummy, and other class who can access the
federated laboratories?

In order to manage users, we have to use the *weblab-admin.py admin* tool. Usually,
you can do it while the server is running. However, in this small deployment, we
are using `sqlite <http://www.sqlite.org/>`_, a small and fast database engine
that does not support concurrent access. Therefore, while using sqlite, we will
need first to stop the application so as to manage users::

   localhost - - [03/Nov/2012 14:48:59] "GET /weblab/client/index.html HTTP/1.1"
   200 -
   localhost - - [03/Nov/2012 14:49:00] "POST /weblab/json/ HTTP/1.1" 200
   (enter)
   Stopping servers...
   $ 

And then, we can run the *weblab-admin.py admin* tool safely::

   $ weblab-admin.py admin example
   ----------------------------------
   - WebLab-Deusto Database Manager -
   ----------------------------------
   
   Main Menu
   
    1. Add Group
    2. Add Experiment Category
    3. Add Experiment
    4. Add Users to Group using a file
    5. Add User to Group
    6. Add User with DB AuthType
    7. Add Users with LDAP AuthType
    8. Add Users with OpenID AuthType
    9. Add Users (batch) with DB AuthType
    10. Grant on Experiment to Group
    11. Grant on Experiment to User
    12. Grant on Admin Panel to Group
    13. Grant on Admin Panel to User
    14. Grant on Access Forward to Group
    15. Grant on Access Forward to User
    16. List Users
    17. Notify users
    18. Notify users (With passwords)
   
   0. Exit
   
   Option: 

This menu depends on the particular version we're running. Upgrading the system
may add more options, and therefore the numbers that will be presented in this
tutorial might easily be not updated. Therefore, take a look at what are the
options in the menu rather than what are the numbers pressed.

In WebLab-Deusto, permissions are granted to users or groups. A particular user
may not be part of any group and still get certain permissions. This especially
applies to special users who represent other organizations (such as *University
of Deusto*). However, when managing students, the common scheme is to create a
group for each class and grant permissions on that group. Let's start with a
simple group of *Electronics-2012_2013*. First, for the sake of clarity, let's
create a 2012-2013 group, for all the groups of this course::

  Option: 1
  
  ----------------------------------
  - WebLab-Deusto Database Manager -
  ----------------------------------
     type '[back]' to go back

  Add Group

  Name: 2012-2013

   1. Administrators
  Parent Group [default: <null>]: 
  
  Group created:
  DbGroup(id = 2, name = '2012-2013', parent = '<None>')
  
  Press any key to continue...
 
Then, let's create a child group of this group::

  Option: 1 

  ----------------------------------
  - WebLab-Deusto Database Manager -
  ----------------------------------
       type '[back]' to go back
  
  Add Group
  
  Name: Electronics-2012_2013
  
   1. Administrators
   2. 2012-2013
  Parent Group [default: <null>]: 2
  
  Group created:
  DbGroup(id = 3, name = 'Electronics-2012_2013', parent = '<2012-2013>')
  
  Press any key to continue...

Finally, let's create a sample user, called John Doe, using a database (DB)::

  Option: 6

  ----------------------------------
  - WebLab-Deusto Database Manager -
  ----------------------------------
       type '[back]' to go back
  
  Add User with DB AuthType
  
  Login: jdoe
  Full name: John Doe
  Email: jdoe@example.com
  Avatar [default: <null>]: 
  
   1. administrator
   2. professor
   3. student
  Role [default: <null>]: 3
  
   1. WebLab DB
  Auth: 1
  Password [default: <null>]: 
  Password (verify) [default: <null>]: 
  
  User created:
  DbUser(id = 2, login = 'jdoe', full_name = 'John Doe', email = 'jdoe@example.com', avatar = 'None', role = DbRole(id = 3, name = 'student'))
  
  UserAuth created:
  DbUserAuth(id = 2, user = DbUser(id = 2, login = 'jdoe', full_name = 'John Doe', email = 'jdoe@example.com', avatar = 'None', role = DbRole(id = 3, name = 'student')), auth = DbAuth(id = 1, auth_type = DbAuthType(id = 1, name = 'DB'), name = 'WebLab DB', priority = 1, configuration = 'None'), configuration = '************************************************')
  
  Press any key to continue...

From this moment, if we exit the administrator, and we start the WebLab-Deusto
instance, we will be able to log in with that user and password. However, it
will not be able to use any laboratory, since no permission has been granted.
Let's add him to the *Electronics-2012_2013* group first::

  Option: 5

  ----------------------------------
  - WebLab-Deusto Database Manager -
  ----------------------------------
       type '[back]' to go back
  
  Add Users to Group
  
  
   1. admin
   2. jdoe
  User: 2
  
   1. Administrators
   2. 2012-2013
   3. Electronics-2012_2013
  Group: 3
  
  The following Users have been added to the Group:
  DbGroup(id = 3, name = 'Electronics-2012_2013', parent = '<2012-2013>')
  
  DbUser(id = 2, login = 'jdoe', full_name = 'John Doe', email = 'jdoe@example.com', avatar = 'None', role = DbRole(id = 3, name = 'student'))
  
  Total added Users: 1
  
  Press any key to continue...

And let's grant permissions on this group to access the dummy laboratory::

  Option: 10
  
  ----------------------------------
  - WebLab-Deusto Database Manager -
  ----------------------------------
       type '[back]' to go back
  
  Grant on Experiment to Group
  
  
   1. Administrators
   2. 2012-2013
   3. Electronics-2012_2013
  Group: 3
  
   1. dummy@Dummy experiments
   2. external-robot-movement@Robot experiments
  Experiment: 1
  Time allowed: 200
  Priority (0-10, lower is more priority) [default: 5]: 
  
   1. yes
   2. no
  For the time allowed, you are counting with initialization?: 1
  
  GroupPermission created:
  [...]
  
  Press any key to continue...

From this moment, jdoe is a member of the group Electronics-2012_2013, which has
permissions to use the dummy laboratory for 200 seconds (1 minute, 40 seconds),
with a priority = 5. Therefore, if we stop the administrator now and start the
server, we will see how that user indeed can access that laboratory for that
time.

We have created our first user using the interactive mode. If we wanted to add
30 users, this can be easier. The first way is to create a text file
(technically, a CSV file -so you can even use Microsoft Excel-), using the
following format::

  user1, User One, userone@users.com, users1password
  user2, User Two, usertwo@users.com, users2password
  user3, User Three, userthree@users.com, users3password
  user4, User Four, userfour@users.com, users4password
  user5, User Five, userfive@users.com, users5password
  user6, User Six, usersix@users.com, users6password
  user7, User Seven, userseven@users.com, users7password
  user8, User Eight, usereight@users.com, users8password
  user9, User Nine, usernine@users.com, users9password
  user10, User Ten, userten@users.com, users10password

For adding multiple users at the same time. Place that file in the *example*
directory. And will add them all::

  Option: 9

  ----------------------------------
  - WebLab-Deusto Database Manager -
  ----------------------------------
       type '[back]' to go back
  
  Add Users (batch) with DB AuthType
  
  Users file [default: USERSDB]: USERS
   ['user1', 'User One', 'userone@users.com', 'users1password']
   ['user2', 'User Two', 'usertwo@users.com', 'users2password']
   ['user3', 'User Three', 'userthree@users.com', 'users3password']
   ['user4', 'User Four', 'userfour@users.com', 'users4password']
   ['user5', 'User Five', 'userfive@users.com', 'users5password']
   ['user6', 'User Six', 'usersix@users.com', 'users6password']
   ['user7', 'User Seven', 'userseven@users.com', 'users7password']
   ['user8', 'User Eight', 'usereight@users.com', 'users8password']
   ['user9', 'User Nine', 'usernine@users.com', 'users9password']
   ['user10', 'User Ten', 'userten@users.com', 'users10password']
  
   1. administrator
   2. professor
   3. student
  Role [default: <null>]: 3

  [...] 

  Press any key to continue...

And they will be registered in the system. This way, now you can use *user1* and
*users1password* as credentials to log in the system. So as to add them to the
existing group (or to other group), we will need a different text file with a
single column of the existing user names, such as::

  user1
  user2
  user3
  user4
  user5
  user6
  user7
  user8
  user9
  user10

You can place the file in the *example* directory, then add them to the group we
already created by running::

  Option: 4

  ----------------------------------
  - WebLab-Deusto Database Manager -
  ----------------------------------
       type '[back]' to go back
  
  Add Users to Group
  
  Users file [default: USERS]: ../USERS2
   user1
   user2
   user3
   user4
   user5
   user6
   user7
   user8
   user9
   user10
  
   1. Administrators
   2. 2012-2013
   3. Electronics-2012_2013
  Group: 3

  The following Users have been added to the Group:
  DbGroup(id = 3, name = 'Electronics-2012_2013', parent = '<2012-2013>')
  
  DbUser(id = 3, login = 'user1', full_name = 'User One', email = 'userone@users.com', avatar = 'None', role = DbRole(id = 3, name = 'student'))

  [...]

  Total added Users: 10
  
  Press any key to continue...

From this point, all these users will be part of that group, and they will
therefore have permissions to use the dummy laboratory.

Furthermore, WebLab-Deusto supports other authentication schemes (LDAP, OpenID,
OAuth), but they require installing more components (libraries) and they are not
supported in this simple deployment.


Tracking users
~~~~~~~~~~~~~~

Now you can start again the WebLab-Deusto instance, and you can use the
laboratory with different users. Once you have used it several times, you can
log out and go to the Administration panel (the link is under the log in panel),
and open it with the *admin* user. The rest of the users can not access unless
you explicitly put them in the Administrators group or grant them permission to
use it. Once you log in the Administration panel, you will see who has accessed
when:

.. image:: /_static/admin_panel_users.png
   :width: 500 px
   :align: center

Furthermore, in the figure above you can the *admin* user had already used the
system. You can use the filters of the top bar to filter by group, laboratory or
dates. For instance, in the figure below, only the course students are displayed:

.. image:: /_static/admin_panel_group.png
   :width: 500 px
   :align: center


Monitoring users
~~~~~~~~~~~~~~~~

You can also check in real time who is using the system, what is the position of
the queues, etc., by using the *weblab-admin.py monitor* command. While the system
is started and running, you can call from other terminal::

  $ weblab-admin.py monitor example -e
  dummy@Dummy experiments
  external-robot-movement@Robot experiments

To see the active laboratories. If you want to see who is using a particular
laboratory, you can call::

  $ weblab-admin.py monitor example -u "dummy@Dummy experiments"
  Server 1
            LOGIN                    STATUS    UPS_SESSID   RESERV_ID
            user1            reserved_local   4efeaf0a... Session ID: '4efeaf0a-abe6-407f-be9f-82f1271510df'...
            user5                waiting: 0   1e38293d... Session ID: '1e38293d-8775-4740-9516-060a71af8675'...

Waiting: 0 means that this user is in the first slot of the queue. Other users
with the same or lower priorities will be in positions 1, 2, 3, etc. If you need
further information, you can pass the -f flag::

  $ weblab-admin.py monitor example -u "dummy@Dummy experiments" -f
  Server 1
            LOGIN                    STATUS    UPS_SESSID   RESERV_ID
            user1            reserved_local   4efeaf0a-abe6-407f-be9f-82f1271510df    Session ID: '4efeaf0a-abe6-407f-be9f-82f1271510df'
            user5                waiting: 0   1e38293d-8775-4740-9516-060a71af8675    Session ID: '1e38293d-8775-4740-9516-060a71af8675'

Furthermore, you can even kick a particular user (such as user1 in this case,
who is using the system), and check how the queue advances::

  $ weblab-admin.py monitor example -b user1
  Server 1
  $ weblab-admin.py monitor example -u "dummy@Dummy experiments" -f
  Server 1
            LOGIN                    STATUS    UPS_SESSID   RESERV_ID
            user5            reserved_local   1e38293d-8775-4740-9516-060a71af8675    Session ID: '1e38293d-8775-4740-9516-060a71af8675'


Customizing the deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section, we have presented a very simple deployment. However, this
deployment can be configured. While in the `next section
<installation_further>`, we'll learn to configure `redis <http://redis.io/>`_,
`MySQL <http://www.mysql.com/>`_ or `Apache <http://httpd.apache.org/>`_, there
are some settings that we can modify at this level.

Running::

  $ weblab-admin.py create --help

Displays the full help regarding the create command. A more advanced example
would be::

  $ weblab-admin.py create other.example --http-server-port=8001 --start-port=20000 \
  --system-identifier='My example' --entity-link='http://www.myuniversity.edu/'  \
  --poll-time=300 --admin-user=administrator --admin-name='John Doe'             \
  --admin-password=secret --admin-mail='admin@weblab.myuniversity.edu' --logic

This example will be run in other port (8001), so you can start it at the same
time as the other deployment without problems. Just go to
`http://localhost:8001/ <http://localhost:8001/>`_ instead, log in with user
*administrator* and password *secret*, and see how there is another laboratory
called *logic*.

Other examples, such as using Virtual Machines, VISIR, etc., are documented in
the :ref:`next section <installation_further>`.
