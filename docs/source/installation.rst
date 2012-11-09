.. _toctree-directive:
.. _installation:

Installation
============

Installing the core of WebLab-Deusto is pretty straightforward. It does not have
many requirements. However, supporting more features and tuning the performance
requires installing more software infrastructure.

Through this tutorial, we'll go through the most simple deployment possible. It
will not require any web server (such as Apache), neither a database engine
(such as MySQL). Instead it will use its internal web server and a simple sqlite
database.  Then, we will explain how to go deep to more complex deployments.

**Note:** during the whole documentation, some examples of commands run in a
terminal will be presented. Given that terminals are different from system to
system, we will show *$* to represent the terminal prompt. For instance, the
following example::

    $ weblab-admin.py --version
    5.0

The *$* will represent *C:\\something>* in Windows environments and
*user\@machine:directory$* in certain UNIX environments. You must not write that.
Whenever there is no *$* in the beginning of the line (such as *5.0* in the
example), is the expected output. Finally, sometimes the output is too long, so
*[...]* is used to declare "a long output will be shown".

Obtaining WebLab-Deusto
~~~~~~~~~~~~~~~~~~~~~~~

At the time of this writing, there are two ways to obtain WebLab-Deusto:

#. Downloading it from github using the web browser. That's the simplest and **easiest** version. Just go to the `github repository <https://github.com/porduna/weblabdeusto>`_ and click on the ZIP link. Uncompress the file. 
    * **Windows users:** in certain versions of Microsoft Windows, sometimes there are problems with too-long file paths, so if any problem is reported by your uncompressing program, just make sure that the directory where you are uncompressing WebLab is not very long (for instance, uncompressing it in *C:\\weblab* or *C:\\Users\\Tom\\weblab* will surely work, whereas downloading it in *C:\\Users\\My full name\\Downloads\\Other downloads\\Yet other downloads\\weblabdeusto-long-name* might fail).

.. image:: /_static/download_weblabdeusto_zip.png
   :width: 300 px
   :align: center

2. Downloading it from github using git. That's the **recommended** version, since that allows you to upgrade WebLab-Deusto automatically in the future, and even contribute easily. However, it requires installing git. This process is detailed in :ref:`sec-download-git`.


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
#. At this step, you should be able to open a terminal (in Microsoft Windows, click on the Start menu -> run -> type *cmd*) and test that both tools are installed.

Run the following (don't take into account the particular versions, these are just examples)::

  $ python --version 

  Python 2.7.3

  $ javac -version

  javac 1.6.0_24

5. Install setuptools following `the instructions <http://pypi.python.org/pypi/setuptools#installation-instructions>`_. It should be as simple as downloading and executing a file.
#. Once setuptools are installed, you can install *pip* and *virtualenv*. 

In Linux systems you can get them in the package repositories (e.g. in Ubuntu they are python-pip and python-virtualenv), but in other systems you can install them by running::

  $ easy_install pip

  $ easy_install virtualenv

7. At this point, you should be able to open a terminal and test that both tools are installed.

Run the following (don't take into account the particular versions)::

  $ pip --version

  pip 1.0 from /usr/lib/python2.7/dist-packages (python 2.7)

  $ virtualenv --version

  1.7.1.2

Installing WebLab-Deusto
~~~~~~~~~~~~~~~~~~~~~~~~

Create a virtualenv. In UNIX systems (Linux, Mac OS X)::

  user@machine:/opt/weblabdeusto$ cd WHEREVER-IS-WEBLAB (e.g. /opt/weblabdeusto/ )

  user@machine:/opt/weblabdeusto$ virtualenv env

  user@machine:/opt/weblabdeusto$ . env/bin/activate

  (env) user@machine:/opt/weblabdeusto$

In Microsoft Windows environments::

  C:\> cd WHEREVER-IS-WEBLAB (e.g. C:\weblabdeusto\ )

  C:\weblabdeusto> virtualenv env

  C:\weblabdeusto> .\env\Scripts\activate

  (env) C:\weblabdeusto> 

And then, install WebLab-Deusto::

  $ python setup.py install
  [...]
  Finished processing dependencies for weblabdeusto==5.0

The first time you run this, it will take several minutes, and it will require a
lot of available RAM memory. If you ever change anything on the client or you
upgrade the system through git, and you want to re-install it, go to the
*client* directory and run *./gwtc.sh* in UNIX systems or *gwtc* in Microsoft
Windows environments.

Once the process is over, you can test the installation by running::

  $ weblab-admin.py --version
  5.0

**Note for UNIX systems:** The command *weblab-admin* does not work on Microsoft
Windows itself, and therefore the command *weblab-admin.py* is provided for both
frameworks. However, in UNIX you're safe to use *weblab-admin* wherever we
establish *weblab-admin.py* in the whole documentation.

If it displays 5.0 or higher, then you have successfully installed the system in
that virtual environment. Virtual environments in Python are environments where
a set of libraries (with particular versions) are installed. For instance, you
may have different virtual environments for different applications relying on
different versions of libraries. There are even highly recommendable `tools for
managing virtual environments
<http://www.doughellmann.com/projects/virtualenvwrapper/>`_ (and `versions for
Microsoft Windows <http://pypi.python.org/pypi/virtualenvwrapper-win/>`_) which
make this management even easier.

Whenever you open a new terminal, you'll find that *weblab-admin.py* is not
installed. However, whenever you activate the environment where you installed
WebLab-Deusto, it will be installed. For instance, if you open a new terminal,
do the following in UNIX systems::

    user@machine:~$ . /opt/weblabdeusto/env/bin/activate
    (env) user@machine:~$ weblab-admin.py --version
    5.0

Or the following in Microsoft Windows systems::

    C:\Users\John\Desktop> C:\weblabdeusto\env\Scripts\activate
    (env) C:\Users\John\Desktop> weblab-admin.py --version
    5.0

Now you can continue with the :ref:`first steps <first_steps>`.
