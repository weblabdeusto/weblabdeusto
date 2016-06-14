.. _weblabdeusto_development:

WebLab-Deusto development
=========================

.. contents:: Table of Contents

Introduction
------------

This section covers documentation about how to work on the WebLab-Deusto development. If you want to develop a remote laboratory instead of working in the middle layers, go to the :ref:`remote_lab_development` section.

Setting up the development environment
--------------------------------------

This section assumes that you have successfully used the steps refered in the :ref:`installation_further` section.

Server side
^^^^^^^^^^^

When developing the server side, it is best to create a new environment on which WebLab-Deusto is not deployed. To do so, create a new virtualenv as explained in :ref:`installation`, and install all the requirements, but do not run the ``python setup.py install`` command.

So as to deploy the testing database (required to pass the tests), you need to run the following in the ``weblab/server`` directory::

    python develop.py --deploy-test-db --db-engine=mysql --db-create-db --db-ask-admin-passwd

Once you do this, you will be able to launch the server side tests, by running::

    python develop.py

If you are developing and you think you want to do some static analysis of your code, run the following::

    python develop.py --flakes

Finally, the ``develop.py`` script comes with many more options. Run the following to see them::

    python develop.py --help


Sample environment
^^^^^^^^^^^^^^^^^^

.. note::

    To be written, but you may go to the ``server/launch`` directory and find many testing deployments. The ``sample`` one is especially interesting, since whenever you make a change in the Python code, it is automatically restarted.


Contributing
------------

There are plenty of issues in the `issue tracker at github <https://github.com/weblabdeusto/weblabdeusto/issues/>`_. You may add new ones if you find things to change, but you may also take the existing ones an fix them by your own.

Take a look at :ref:`contributing` to find other ways to contribute to the project.
