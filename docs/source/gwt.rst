.. _gwt:

Compilation of the legacy client labs
=====================================

Installation
~~~~~~~~~~~~

#. Install the Java Development Kit:
    * In Linux, use the repositories of your distribution. In Ubuntu, you can install the openjdk-6-jdk package.
    * In Mac OS X, install `XCode <https://developer.apple.com/xcode/>`_.
    * In Microsoft Windows, refer to the `official site <http://www.oracle.com/technetwork/java/javase/downloads/index.html>`_.
#. Once installed, put it in the system path:
    * In Linux and Mac OS X, this is probably done by default.
    * In Microsoft Windows, go to Control Panel -> System -> Advanced -> Environment variables -> (down) PATH -> edit and append: the Java path (which depends on the particular version, it is usually somewhere in ``C:\Program Files\Java\jdkSOMETHING\bin``). Additionally, in Microsoft Windows you'll need to create a new environment variable in the same menu, called ``JAVA_HOME`` and which points to ``C:\Program Files\Java\jdkSOMETHING`` -without bin-).

#. At this step, you should be able to open a terminal (in Microsoft Windows, click on the Start menu -> run -> type ``cmd``) and test that both tools are installed.

Run the following (don't take into account the particular versions, these are just examples)::

  $ javac -version

  javac 1.6.0_24


