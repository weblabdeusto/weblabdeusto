.. _first_steps_cli:

First steps in CLI
==================

In order to manage users using command line, we have to use the *weblab-admin.py admin* tool. Usually,
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
