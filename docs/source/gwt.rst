.. _gwt:

Compilation of the legacy client labs with GWT
==============================================

#. Install the Java Development Kit:
    * In Linux, use the repositories of your distribution. In Ubuntu, you can install the openjdk-6-jdk package.
    * In Mac OS X, install `XCode <https://developer.apple.com/xcode/>`_.
    * In Microsoft Windows, refer to the `official site <http://www.oracle.com/technetwork/java/javase/downloads/index.html>`_.
#. Once installed, put it in the system path:
    * In Linux and Mac OS X, this is probably done by default.
    * In Microsoft Windows, go to Control Panel -> System -> Advanced -> Environment variables -> (down) PATH -> edit and append: the Java path (which depends on the particular version, it is usually somewhere in ``C:\Program Files\Java\jdkSOMETHING\bin``). Additionally, in Microsoft Windows you'll need to create a new environment variable in the same menu, called ``JAVA_HOME`` and which points to ``C:\Program Files\Java\jdkSOMETHING`` -without bin-).

#. At this step, you should be able to open a terminal (in Microsoft Windows, click on the Start menu -> run -> type ``cmd``) and test that both tools are installed.

Run the following (don't take into account the particular versions, these are just examples):

.. code-block:: bash

  $ javac -version

  javac 1.6.0_24

From this point, you might go to the ``server/src`` directory of the source code (that you downloaded through git), and compile the legacy GWT client:

.. code-block:: bash

   $ cd weblab/server/src
   $ workon weblab
   (weblab) $ python develop.py --compile-gwt-client
   [...]
   (weblab) $ 

The process might take several minutes (even half an hour depending on your computer). If you had previuosly compiled the client, it might tell you to force the compilation providing you instructions on how to re-compile it.

Once compiled, you have to run the following script:

.. code-block:: bash

   (weblab) $ python setup.py install

After this script finishes (it will essentially copy the client to the appropriate folder of WebLab-Deusto), the GWT client will have been properly installed.
