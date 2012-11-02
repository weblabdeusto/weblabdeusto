.. _toctree-directive:

Installation
============

Installing the core of WebLab-Deusto is pretty straightforward. It does not have
many requirements. However, supporting more features and tuning the performance
requires installing more software infrastructure.

Through this tutorial, we'll go through the most simple deployment possible.
Then, we will explain how to go deep to more complex deployments.

Obtaining WebLab-Deusto
~~~~~~~~~~~~~~~~~~~~~~~

At the time of this writing, there are two ways to obtain WebLab-Deusto:

#. Downloading it from github using the web browser. That's the simplest version. Just go to the `github repository <https://github.com/porduna/weblabdeusto>`_ and click on the ZIP link. Uncompress the file. 
    * **Windows users:** in certain versions of Microsoft Windows, sometimes there are problems with too-long file paths, so if any problem is reported by your uncompressing program, just make sure that the directory where you are uncompressing WebLab is not very long (for instance, uncompressing it in *C:\\weblab* or *C:\\Users\\Tom\\weblab* will surely work, whereas downloading it in *C:\\Users\\My full name\\Downloads\\Other downloads\\Yet other downloads\\weblabdeusto-long-name* might fail).

.. image:: /_static/download_weblabdeusto_zip.png
   :width: 300 px
   :align: center

2. Downloading it from github using git. That's the recommended version, since that allows you to upgrade WebLab-Deusto automatically in the future, and even contribute easily. However, it requires installing git. This process is detailed in :ref:`sec-download-git`.


Installing the requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Install Python 2.7:
    * In Linux and Mac OS X, Python is probably installed.
    * In Microsoft Windows, download it `from here <http://www.python.org/download/>`_. Do not download Python 3.x (WebLab-Deusto relies on Python 2.7).
#. Install the Java Development Kit:
    * In Linux, use the repositories of your distribution. In Ubuntu, you can install the openjdk-6-jdk package.
    * In Microsoft Windows and Mac OS X, refer to the `official site <http://www.oracle.com/technetwork/java/javase/downloads/index.html>`_.
#. Once installed, put both in the system path:
    * In Linux and Mac OS X, this is probably done by default.
    * In Microsoft Windows, go to Control Panel -> System -> Advanced -> Environment variables -> (down) PATH -> edit and append: *;C:\Python27\;C:\Python27\Scripts\;*, as well as the Java path (which depends on the particular version, it is usually somewhere in *C:\Program Files\Java\jdkSOMETHING\bin*).
#. At this step, you should be able to open a terminal (in Microsoft Windows, click on the Start menu -> run -> type *cmd*) and run (don't take into account the particular versions, these are just examples)::

  $ python --version 

  Python 2.7.3

  $ javac -version

  javac 1.6.0_24

#. Install setuptools following `the instructions <http://pypi.python.org/pypi/setuptools#installation-instructions>`_. It should be as simple as downloading and executing a file.
#. Once installed, open a terminal and run::

  $ easy_install pip

  $ easy_install virtualenv

#. At this point, you should be able to open a terminal and run (don't take into account the particular versions)::

  $ pip --version

  pip 1.0 from /usr/lib/python2.7/dist-packages (python 2.7)

  $ virtualenv --version

  1.7.1.2

Installing WebLab-Deusto
~~~~~~~~~~~~~~~~~~~~~~~~

Create a virtualenv. In UNIX systems (Linux, Mac OS X)::

  $ cd WHEREVER-IS-WEBLAB (e.g. /opt/weblabdeusto/ )

  $ virtualenv env

  $ . env/bin/activate

In Microsoft Windows environments::

  C:\> cd WHEREVER-IS-WEBLAB (e.g. C:\weblabdeusto\ )

  C:\weblabdeusto> virtualenv env

  C:\weblabdeusto> .\env\Scripts\activate

  (env) C:\weblabdeusto> 

And then, install WebLab-Deusto::

  $ python setup.py install

This process will take several minutes. Once this process is finished, you can safely run::

  $ weblab-admin create my-instance

To create a WebLab-Deusto instance. You can then manage that instance with the weblab-admin script.

