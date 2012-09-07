Introduction
============

`WebLab-Deusto <http://www.weblab.deusto.es>`_ is a remote laboratory management
framework developed in the `University of Deusto <http://www.deusto.es>`_. A
remote laboratory is a software and hardware solution that enables students to
access equipment which is physically located in a university, secondary school
or research centre.  There are many types of remote laboratories (for physics,
chemistry, electronics...). What WebLab-Deusto does is:

#. provide a set of APIs to develop new remote laboratories.
#. maintain remote laboratories developed on top of WebLab-Deusto: manage users,
   permissions, user tracking, scheduling, etc.
#. share remote laboratories developed on top of WebLab-Deusto: let other
   universities or secondary schools use your laboratories.
#. use remote laboratories provided by other universities (such as the
   University of Deusto).

If you want to see examples of running laboratories, try the demo version at:

   http://www.weblab.deusto.es/weblab/

Documentation
=============

The full documentation of WebLab-Deusto prior to WebLab-Deusto 5 is available in:

   http://code.google.com/p/weblabdeusto/

Please take into account that this documentation can not be applied to the
current development version of WebLab-Deusto, and certain things are different.
We are working on a new version of the documentation. In the meanwhile, please
refer to the `Google Group
<https://groups.google.com/forum/?fromgroups#!forum/weblabdeusto>`_ to ask any
question.

Installation
============

The full instructions to install the development version are `here
<code.google.com/p/weblabdeusto/wiki/4_5_Developers>`_. However,
the quick version is:

#. Install `Python 2.7 <http://www.python.org/download/>`_ and the `Java Development Kit 6 <http://www.oracle.com/technetwork/java/javase/downloads/index.html>`_.
#. Install `setuptools <http://pypi.python.org/pypi/setuptools>`_, `pip <http://www.pip-installer.org/en/latest/installing.html#using-the-installer>`_ and `virtualenv <http://www.virtualenv.org/en/latest/index.html#installation>`_.

Create a virtualenv and then install it::

  $ python setup.py install

From this point, you can run::

  $ weblab-admin create my-instance

To create a WebLab-Deusto instance. You can then manage that instance with the weblab-admin script.

Contact
=======

For technical issues, please use the Google Group:

   https://groups.google.com/forum/?fromgroups#!forum/weblabdeusto

For contacting the WebLab-Deusto team, contact us at:

   `weblab@deusto.es <mailto:weblab@deusto.es>`_

