.. _installation:

Installation
============

Installing the core of WebLab-Deusto is pretty straightforward. It does not have
many requirements. However, supporting more features and tuning the performance
requires installing more software infrastructure. This section covers only the first
steps.

.. note::

    If you're familiar with ``Python``, ``git``, ``setuptools`` and
    ``virtualenv``, all you need to do (in a ``virtualenv``) is::
        
        pip install git+https://github.com/weblabdeusto/weblabdeusto.git

    And go :ref:`to the next section <first_steps>`. Please note that, given
    the size of the repository, it's better if you keep the weblabdeusto git
    repository downloaded in your computer so you can call ``git pull`` to 
    upgrade faster.

    Otherwise, please read this section.

Through this tutorial, we'll go through the most simple deployment possible. It
will not require any web server (such as Apache), neither a database engine
(such as MySQL). Instead it will use its internal web server and a simple sqlite
database.  Then, we will explain how to go deep to more complex deployments.

**Note:** during the whole documentation, some examples of commands run in a
terminal will be presented. Given that terminals are different from system to
system, we will show ``$`` to represent the terminal prompt. For instance, the
following example:

.. code-block:: bash

    $ weblab-admin --version
    5.0

The ``$`` will represent ``C:\something>`` in Windows environments and
``user@machine:directory$`` in certain UNIX environments. You must not write that.
Whenever there is no ``$`` in the beginning of the line (such as ``5.0`` in the
example), is the expected output. Finally, sometimes the output is too long, so
``[...]`` is used to declare "a long output will be shown".

Obtaining WebLab-Deusto
~~~~~~~~~~~~~~~~~~~~~~~

There are two ways to obtain WebLab-Deusto:

#. Downloading it from github using git. That's the **recommended** version, since that allows you to upgrade WebLab-Deusto automatically in the future, and even contribute easily. However, it requires installing git. 
    * This process is detailed in :ref:`sec-download-git`.
#. Downloading it from github using the web browser. That's the simplest version, but we **do not recommend it** (since you lose useful information about the running version and the upgrade process is very complicated). If you still try to use it, go to the `github repository <https://github.com/weblabdeusto/weblabdeusto>`_ and click on the ZIP link. Uncompress the file. 
    * **Windows users:** in certain versions of Microsoft Windows, sometimes there are problems with too-long file paths, so if any problem is reported by your uncompressing program, just make sure that the directory where you are uncompressing WebLab is not very long (for instance, uncompressing it in ``C:\weblab`` or ``C:\Users\Tom\weblab`` will surely work, whereas downloading it in ``C:\Users\My full name\Downloads\Other downloads\Yet other downloads\weblabdeusto-long-name`` might fail).

.. image:: /_static/download_weblabdeusto_zip.png
   :width: 300 px
   :align: center

.. _installation_requirements:

Installing the requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Install Python 2.7:
    * In Linux and Mac OS X, Python is probably installed.
    * In Microsoft Windows, download it `from here <http://www.python.org/download/>`_. Do not download Python 3.x (WebLab-Deusto relies on Python 2.7).
#. Once installed, put both in the system path:
    * In Linux and Mac OS X, this is probably done by default.
    * In Microsoft Windows, go to Control Panel -> System -> Advanced -> Environment variables -> (down) PATH -> edit and append: ``;C:\Python27\;C:\Python27\Scripts\;``.
#. At this step, you should be able to open a terminal (in Microsoft Windows, click on the Start menu -> run -> type ``cmd``) and test that both tools are installed.

Run the following (don't take into account the particular versions, these are just examples):

.. code-block:: bash

  $ python --version 

  Python 2.7.6

4. Install ``setuptools`` if you don't have them. In Windows, nowadays the installer of Python comes with ``pip``, so you don't need to install anything else. In Linux, you usually can install it from the repositories (e.g., ``sudo apt-get install python-pip virtualenv virtualenvwrapper`` in Ubuntu/Debian). If in doubt, follow `the instructions <https://pypi.python.org/pypi/setuptools#installation-instructions>`_. In any system, make sure you also install ``virtualenv`` and ``virtualenvwrapper`` (in Ubuntu you can use the command mentioned ``sudo apt-get install virtualenv virtualenvwrapper``). In particular, in Windows run the following:

.. code-block:: console

   C:\> pip install virtualenvwrapper-win

5. At this point, you should be able to open a terminal and test that these tools are installed.

Run the following (don't take into account the particular versions):

.. code-block:: bash

  $ pip --version

  pip 1.5.4 from /usr/lib/python2.7/dist-packages (python 2.7)

  $ virtualenv --version

  1.11.4

  $ mkvirtualenv --version

  1.11.4

Troubleshooting
```````````````

virtualenv and virtualenvwrapper **are not strictly necessary**. If you don't use
them, you can always install WebLab-Deusto at system level (using administrator
credentials. So if you get problems that you can not solve when installing
virtualenv, do not worry and skip that step.

That said, there are some common problems installing virtualenvwrapper, listed
here:

* **mkvirtualenv: command not found**: virtualenvwrapper is a bash script, which
  must be loaded. By default in Ubuntu, it is correctly loaded in all the new
  terminals, so try closing the current terminal and opening it again. If the
  problem persists, you may need to find where is a script called
  ``virtualenvwrapper.sh``, and add to your ``~/.bashrc``:


.. code-block:: bash

  source /path/to/virtualenvwrapper.sh


* Problems in **Microsoft Windows Windows** with path not found: Check that you
  have installed virtualenvwrapper-win and not virtualenvwrapper.

If you still have problems with ``mkvirtualenv``, try uninstalling it (``pip
uninstall virtualenvwrapper``) and installing only the ``virtualenv`` package.
If you do this, you will need to do:

.. code-block:: bash

  $ virtualenv weblab_env
  New python executable in weblab_env/bin/python
  Installing distribute....................done.
  Installing pip...............done.
  $ 

And then, each time you want to workin the virtualenv, run:

.. code-block:: bash

  (On UNIX)
  $ ./weblab_env/bin/activate
  (weblab_env) user@machine:~$

  (On Windows)
  C:\> .\weblab_env\Scripts\activate
  (weblab_env) C:\> 

If this also generates problems, you can safely avoid using a virtual
environment and install the whole system as administrator.

Installing WebLab-Deusto
~~~~~~~~~~~~~~~~~~~~~~~~

Create a virtualenv. In UNIX systems:

.. code-block:: bash

  user@machine:/opt/weblabdeusto$ cd WHEREVER-IS-WEBLAB (e.g., /opt/weblabdeusto/ )

  user@machine:/opt/weblabdeusto$ mkvirtualenv weblab

  (weblab) user@machine:/opt/weblabdeusto$

In Microsoft Windows environments:

.. code-block:: batch

  C:\> cd WHEREVER-IS-WEBLAB (e.g., C:\weblabdeusto\ )

  C:\weblabdeusto> mkvirtualenv weblab

  (weblab) C:\weblabdeusto> 

And then, install WebLab-Deusto:

.. code-block:: bash

  $ python setup.py install
  [...]
  Finished processing dependencies for weblabdeusto==5.0

Once the process is over, you can test the installation by running:

.. code-block:: bash

  $ weblab-admin --version
  5.0 - 1ac2e2b03048cf89c8df36c838130212f4ac63d3 (Sunday, October 18, 2015)

If it displays 5.0 or higher, then you have successfully installed the system in
that virtual environment. Virtual environments in Python are environments where
a set of libraries (with particular versions) are installed. For instance, you
may have different virtual environments for different applications relying on
different versions of libraries. The long code (i.e., 1ac2e2...) refers to the 
currently installed version, and then the date of the latest change in the 
WebLab-Deusto repository. You should :ref:`upgrade the system <upgrade>` from time 
to time to obtain the latest features.

Whenever you open a new terminal, you'll find that ``weblab-admin`` is not
installed. However, whenever you activate the environment where you installed
WebLab-Deusto, it will be installed. For instance, if you open a new terminal,
do the following in UNIX systems:

.. code-block:: bash

    user@machine:~$ workon weblab
    (weblab) user@machine:~$ weblab-admin --version
    5.0 - 1ac2e2b03048cf89c8df36c838130212f4ac63d3 (Sunday, October 18, 2015)

Or the following in Microsoft Windows systems::

    C:\Users\John\Desktop> workon weblab
    (weblab) C:\Users\John\Desktop> weblab-admin --version
    5.0 - 1ac2e2b03048cf89c8df36c838130212f4ac63d3 (Sunday, October 18, 2015)

Now you can continue with the :ref:`first steps <first_steps>`.
