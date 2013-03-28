.. _sec-download-git:

Download using git
==================

.. contents:: Table of Contents

Microsoft Windows
~~~~~~~~~~~~~~~~~

Git is a source control system. It enables you to download the code, keep track of what you have changed (if you make any change), and you can easily download the latest code in the repository. 
There are different visual and command line tools to use Git. Use the tool you're more familiar with. Here we are going to detail the most basic one, which is the standard system (command-line based).

So as to download git for Microsoft Windows, go to the `git official page <http://git-scm.com/download/win>`_. An installer will be downloaded. The installation process is straightforward: you just need to click on "Next" except for one point, which it says "Adjusting your PATH environment". In that step, select the second option ("Run Git from the Windows Command Prompt"):

.. image:: /_static/git-windows.jpg
   :width: 400 px
   :align: center


Once the installation process is finished, you need to open the command prompt ("Start menu" -> "Run" -> type "cmd" and press enter or "Windows menu" -> type "cmd" and press enter). On it, you may run the following::

    C:\Users\John> cd \
    C:\> git clone https://github.com/weblabdeusto/weblabdeusto.git weblab
    Cloning into 'weblabdeusto'...
    remote: Counting objects: 43259, done.
    remote: Compressing objects: 100% (7927/7927), done.
    remote: Total 43259 (delta 31828), reused 42870 (delta 31439)
    Receiving objects: 100% (43259/43259), 47.13 MiB | 315 KiB/s, done.
    Resolving deltas: 100% (31828/31828), done.
    Checking out files: 100% (2729/2729), done.

From this point, you have downloaded the latest version of WebLab-Deusto. If you later wanted to upgrade the system to a new release, you must use the following command::

    C:\Users\John> cd \weblab
    C:\weblab> git pull 
    Already up-to-date.
    C:\weblab>
    
Feel free to try TortoiseGit (a graphical tool), which is open source and you can download it for free `here <http://code.google.com/p/tortoisegit/>`_, and apply the same steps. Github also provides `a useful tool <http://windows.github.com/>`_ for Microsoft Windows, while it requires registration in the system.

After downloading it you can go to the next step: :ref:`installation_requirements`.

Linux
~~~~~

You need to install git. In most Linux distributions, a package is available. For instance, in Ubuntu, you may run::

   user@machine:~$ sudo apt-get install git

If unsure, go to the `GNU/Linux downloads page <http://git-scm.com/download/linux>`_ and follow the instructions. Once installed, you only need to download the source code::

  user@machine:~$ git clone https://github.com/weblabdeusto/weblabdeusto.git weblab

After downloading it you can go to the next step: :ref:`installation_requirements`.

Mac OS X
~~~~~~~~

You need to install git. By going to the `official page <http://git-scm.com/download/mac>`_, you will get an installer and instructions. Once installed, you may open a terminal and run::

  $ git clone http://github.com/weblabdeusto/weblabdeusto.git weblab

After downloading it you can go to the next step: :ref:`installation_requirements`.
