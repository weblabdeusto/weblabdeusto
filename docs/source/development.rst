WebLab-Deusto development
=========================

This section covers documentation about how to work on the WebLab-Deusto development. If you want to develop a remote laboratory instead of working in the middle layers, go to the :ref:`remote_lab_development` section.

.. note::

    To be written. Quick notes:

    * There are over 800 unit and integration tests in the system, both in client and server. 

      * In the server, use the ``server/src/development.py`` tool to run them, to avoid the integration tests, run a particular one, etc. Also use this tool to deploy the testing database server, etc. Check options with ``./development --help``.
      * In the client, use Eclipse to run them, or run ``ant test``.
      * In the ``server/launch`` directory there is a set of WebLab-Deusto testing deployments.
    * You're welcome to fork the system from `github <http://github.com/weblabdeusto/weblabdeusto/>`_ and add contributions.

