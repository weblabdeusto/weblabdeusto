.. _remote_lab_development:

Remote laboratory development
=============================

.. note::
    **This section is being written at this time (October 2015)**

.. contents:: Table of Contents

Introduction
------------

This section covers the development of new remote laboratories using
WebLab-Deusto. As detailed in :ref:`technical_description`, WebLab-Deusto
provides a set of libraries so experiment developers can create their own remote
laboratories.

There are two major approaches for using WebLab-Deusto:

#. Managed laboratories
#. Unmanaged laboratories

Which are described below.

.. note::

    This section explains the provided APIs and tools for development. However,
    you need to read :ref:`the following section <remote_lab_deployment>` to
    register the new laboratory and use it. So you probably need to go from one
    document to the other during the development cycle.

Managed laboratories
^^^^^^^^^^^^^^^^^^^^

Managed laboratories are those laboratories developed with the API of
WebLab-Deusto. They basically have two parts:

* A **client**, developed using one of the libraries provided by WebLab-Deusto (see
  :ref:`below <managed_libraries_client>`).
* A **server**, developed using one of the provided server libraries or using
  XML-RPC directly (see :ref:`below <managed_libraries_server>`).

This way, the client will run on the web browser and will basically display the
user interface. Whenever the user interface requires accessing the equipment, it
will use the provided API to submit a command and retrieve a response. For
example, a typical application might perform an action when the user presses a
button. This button will submit a message (command) using the API, and
WebLab-Deusto will call a particular method in the server side with that
particular message.

Therefore, managed laboratories count with the following advantages:

* Experiment developer does not manage any type of **communications**. The client
  API has a method for submitting a command, which the WebLab-Deusto client will
  propagate as securely as the system has been configured (e.g., supporting SSL)
  to the server, which once in the campus side, the server will submit the
  command to the particular equipment (regardless where it is deployed in the
  internal topology of the campus side network). All commands submitted through
  WebLab-Deusto will go through pure HTTP, crossing firewalls and proxies.
* All the **information is stored** in the database by default, so it is possible to
  perform learning analytics. By default, administrators and instructors be able
  to track what exact commands were submitted by the student. This process
  however does not add a relevant latency, since instead of storing each command
  whenever is sent, it adds it to a memory queue (which is a fast operation),
  and other thread is continuosly retrieving information from the queue and
  storing it in the database in a batch basis.
* Managed laboratories support local **load balancing**. This means that if you ever
  have multiple copies of a laboratory, if the communication goes through the
  WebLab-Deusto API, the client will not need to know which copy is being
  addressed, since the WebLab-Deusto internals will forward the message to the
  laboratory used by the current user.

Given the amount of technologies used in remote laboratories, WebLab-Deusto not
only supports but even provides libraries to support multiple programming
languages. 

Unmanaged laboratories
^^^^^^^^^^^^^^^^^^^^^^

However, not everybody in the remote laboratory community is comfortable with
developing a remote laboratory from scratch by programming. For this reason,
WebLab-Deusto also supports unmanaged laboratories, which are those where the
communication is not sent through WebLab-Deusto, but directly to the final
server.

The two clear examples of this are:

#. **Virtual Machines** based remote laboratories. A VirtualBox (at this moment)
   virtual machine created by the experiment developer is loaded. The virtual
   machine might run a Linux or Windows system, which will be accessed through
   SSH, VNC or Remote Desktop. WebLab-Deusto guarantees that the server will be
   executed.
#. **LabVIEW Remote Panels**. They were developed but they caused too many problems.
   If you are really interested, :ref:`contact us <contact>` and we can create more
   documentation on their support in WebLab-Deusto. But at this stage, it simply
   does not make too much sense. It is much better if you support :ref:`LabVIEW
   as managed <managed_library_server_labview>`.

The main **drawbacks** of unmanaged laboratories is that:

* They might cause problems with **proxies or firewalls**, since the communication
  is managed by the final system.
* The **user tracking** functionality is decreased: WebLab-Deusto still registers
  who uses what and when, but not what the user did during the session.
* The **load balancing** functionality is decreased or even removed.

Additionally, this is more complex to deploy for system administrators.

For these reasons, using the managed approach is desirable, while we maintain
this other approach for those laboratories which are far more difficult to
develop.

Which one should I use?
^^^^^^^^^^^^^^^^^^^^^^^

It depends on your background. 

Managed laboratories
--------------------

This section describes how to develop experiments using the managed model.

Introduction
^^^^^^^^^^^^

As previously defined, in the managed laboratories, all the communications are
managed by WebLab-Deusto. This basically means that, as seen on the following
figure, the client code will call a set of methods such as:

.. code-block:: java

   // In the client side
   weblab.sendCommand("press button1");

And WebLab-Deusto guarantees that this string will be forwarded to the proper
experiment server. In the experiment server, there will be a method such as (in
Java):

.. code-block:: java

    public String sendCommand(String command) throws WebLabException {
        // Manage the command and return the results
        if (command.startsWith("press ")) {
            String what = command.substring("press ".length);
            pressButton(what);
            return getStatus();
        }
    }

So as to do this, WebLab-Deusto provides :ref:`APIs for the client
<managed_libraries_client>`, which wrap the communications submitting the
commands to the server side using HTTP (and HTTPS if available), adding the
required metadata (such as the session identifier). This is *step 1* in the
following figure. Once in the Core server (check :ref:`the technical description
if lost <technical_description>`), it checks if that the session is still
available and with an experiment assigned.  If so, it submits the command to the
Laboratory server in charge of the assigned experiment (there might be different
laboratory servers) and stores the command in the database. This process is
faster than it may sound, since it uses memory structures and internal queues so
there is only a single thread using the database for adding the commands
submitted. This is *step 2* in the figure. Once in the Laboratory server, it
checks to which Experiment server the command should be submitted, and submits
it (this is *step 3*). If the Experiment Server was developed with one of the
:ref:`libraries for servers <managed_libraries_server>`, then this gets the
message in the programming language used and passes it to the Experiment server
code.

.. figure:: /_static/managed_model.png
   :align: center

   Command sent through the managed model. See the diagram `in full size here <_static/managed_model.png>`_.

This way, it is entirely up to the experiment developer to choose the proper
programming environment for its experiments. Furthermore, developers will select
the format of the contents submitted as commands. WebLab-Deusto does not impose
any restriction on this side, so developers may send a simple string such as
``press button1`` that will later parse, or they may use an XML or JSON format.

For this reason, in the case of the managed model, developers do not need to handle:

* Scheduling (the core server manages it)
* Communications (the libraries manage it)
* User tracking (every command is stored in the database)
* Complex deployments (e.g., load balancing: it is configured at WebLab-Deusto
  level)


.. _managed_libraries_client:

Client side
^^^^^^^^^^^

In this section, the client side libraries and approaches for developing remote
laboratories are presented.

Introduction
............

The client code is focused on two tasks:

* Providing the user interface
* Submitting commands to the Experiment server and managing the responses

While WebLab-Deusto supports some web libraries, it is highly recommended to use
libraries which rely on JavaScript (such as JavaScript itself or Google Web
Toolkit). Those laboratories developed on top of these libraries will be
available for mobile devices, and the number of conflicts in different platforms
will be highly decreased, since they will not need any plug-in installed.

In the following sections describe how to use each of the provided APIs.

Google Web Toolkit
..................

`Google Web Toolkit (GWT) <http://developers.google.com/web-toolkit/>`_ is the
technology used by all the remote labs developed by the WebLab-Deusto team. You
are encouraged to use it, while we support the other options.

**Why GWT?**


In GWT, you write code in Java using Eclipse, and it generates optimized
JavaScript code. For instance, it generates the whole application for each of
the supported web browsers (implementing the high level features in different
ways for each one), and translated to each supported language. Therefore, when
you access the web application, you only download the code dependent of your
language and web browser.

The platform is mature and very advanced, providing the following features:

* The `provided widgets
  <http://gwt.googleusercontent.com/samples/Showcase/Showcase.html#!CwCheckBox>`_
  are natively supported in many web browsers.

* It does not wrap *too much:* you can still call native code and export
  functionalities to pure JavaScript using `JSNI
  <https://developers.google.com/web-toolkit/doc/latest/DevGuideCodingBasicsJSNI>`_.
  You can even provide alternatives to widgets, and when compiling the system it
  will use different code for each web browser. For example, in WebLab-Deusto,
  the camera component is different in `Chrome/Safari
  <https://github.com/weblabdeusto/weblabdeusto/blob/0e924c5c16adaf324bb3a3ad27c1fd420412cb71/client/src/es/deusto/weblab/client/ui/widgets/WlWebcamSafariBased.java>`_,
  in `Firefox
  <https://github.com/weblabdeusto/weblabdeusto/blob/0e924c5c16adaf324bb3a3ad27c1fd420412cb71/client/src/es/deusto/weblab/client/ui/widgets/WlWebcamFirefox.java>`_
  or `other web browsers
  <https://github.com/weblabdeusto/weblabdeusto/blob/0e924c5c16adaf324bb3a3ad27c1fd420412cb71/client/src/es/deusto/weblab/client/ui/widgets/WlWebcam.java>`_,
  by simply `defining it in the XML file
  <https://github.com/weblabdeusto/weblabdeusto/blob/0e924c5c16adaf324bb3a3ad27c1fd420412cb71/client/src/es/deusto/weblab/WebLabClient.gwt.xml#L30>`_.

* It supports writing the user interface directly with code, with `a custom XML
  <https://developers.google.com/web-toolkit/doc/latest/DevGuideUiBinder>`_, or
  even with the `GWT Designer
  <https://developers.google.com/web-toolkit/tools/gwtdesigner/userinterface/design_view>`_
  (a visual tool).

* It enables you to easily define how to `split the application
  <https://developers.google.com/web-toolkit/doc/latest/DevGuideCodeSplitting>`_.
  For instance, when you enter in the application, you will download the desktop
  version (and not the mobile version), and no laboratory by default. When you
  click on a laboratory, then you download the client code of that laboratory.
  And with the proper caching configuration in the web server, you will only
  download this once (kept in the cache during the rest of the accesses). Then,
  you will only download the response of the requests, which are commonly small
  JSON objects. This is very suitable for mobile environments.

* It enables you to `embed the images directly in the JavaScript code
  <https://developers.google.com/web-toolkit/doc/latest/DevGuideUiImageBundles>`_,
  therefore avoiding HTTP connections and loading from cache in a faster way.

* The development cycle is fast: with the development mode in Eclipse, you
  refresh the web page and automatically you are using it without compiling the
  whole thing.

* Localizing the `application is very simple
  <https://developers.google.com/web-toolkit/doc/latest/DevGuideI18n>`_. See it
  `in WebLab-Deusto
  <https://github.com/weblabdeusto/weblabdeusto/tree/master/client/src/es/deusto/weblab/client/i18n>`_.

* You program in Java with Eclipse as a regular application. Your tests are in
  `JUnit
  <https://developers.google.com/web-toolkit/doc/latest/DevGuideTesting>`_.

The WebLab-Deusto server is entirely developed in Python. We therefore not use
those communication components or server side stuff of GWT. We use plain HTTP to
communicate all the client requests to the server. So we basically compile all
the application into JavaScript and load it.

.. warning::

    When running it with the development, the communication is being
    proxied by a server component which takes the requests and sends them to
    ``http://localhost/weblab/``. Note that this will not work if you were using a
    custom WebLab-Deusto deployment and you are not using Apache or you are using
    other path.

You have plenty of information in `the official website
<https://developers.google.com/web-toolkit/doc/latest/DevGuide>`, so you are
encouraged to learn there some basics before developing the laboratory.

**How to develop the lab**

The source code is in ``client/src``. The main package is
``es.deusto.weblab.client``, and inside this, all the laboatories are in the
``experiments`` package (`see here
<https://github.com/weblabdeusto/weblabdeusto/tree/master/client/src/es/deusto/weblab/client/experiments>`_).
You can check any, but the binary one is one of the simplest ones. As you `can
see there
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/experiments/binary/BinaryCreatorFactory.java>`_,
you have to create a class which inherits from ``IExperimentCreatorFactory``.
We'll go to this one later. Then you see a package called ``ui``. It contains
both the class inheriting from ``ExperimentBase`` and the different user
interfaces.

First, let's see the class inheriting from ``ExperimentBase``. In this case, it
is called ``BinaryExperiment``. The `ExperimentBase
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/lab/experiments/ExperimentBase.java>`_
class is the one from which all the remote laboratories inherit. It contains
many methods, most of them optinally implemented by the experiment class. The
methods are the following:

.. code-block:: java

    /**
     * User selected this experiment. It can start showing the UI. It can 
     * load the VM used (Adobe Flash, Java VM, Silverlight/Moonlight, etc.), 
     * or define requirements of the (i.e. require 2 files, etc.). It should
     * also show options to gather information that will be sent to the 
     * initialization method of the experiment server, that later will be 
     * retrieved through the {@link #getInitialData()} method. 
     */
    public void initialize(){}

    /**
     * A user, who performed the reservation outside the regular client (in
     * a LMS or a federated environment) is going to start using this 
     * experiment. Basically it is like the {@link #initialize()} method, 
     * except for that it should be very fast, and take into account that no
     * configuration can be provided (since the reservation has already been 
     * done). 
     */
    public void initializeReserved(){
        initialize();
    }

    /**
     * Retrieves information sent to the experiment when reserving the 
     * experiment. It might have been collected in the UI of the 
     * {@link #initialize()} method.
     */
    public JSONValue getInitialData(){
        return null;
    }

    /**
     * User is in a queue. Thetype filter text typical behavior will be to hide the UI shown
     * in the {@link #initialize()} method. 
     */
    public void queued(){}

    /**
     * User grabs the control of the experiment (in the server side, the 
     * experiment is already reserved for the user).
     * 
     * @param time Seconds remaining. This time is the maximum permission time.
     * @param initialConfiguration Data sent by the experiment server in the 
     * initialization method.
     */
    public void start(int time, String initialConfiguration){}

    /**
     * User experiment session finished. The experiment should clean 
     * its resources, or notify the user that it has finished. It may still
     * wait for the {@link #postEnd(String)} method to be called so as to
     * receive the information sent by the experiment when disposing 
     * resources.
     */
    public void end(){}

.. /* (this is to avoid highlight problems in vim)

Therefore, it is up to the Experiment client to do something when these methods
are called. Most typically, developers will implement the ``start`` method and
the ``end`` method. Additionally, all the classes inheriting from
``ExperimentBase`` also inherit the following attributes:

.. code-block:: java

    protected final IBoardBaseController boardController;
    protected final IConfigurationRetriever configurationRetriever;
    protected static final IWebLabI18N i18n = GWT.create(IWebLabI18N.class);

The first one allows developers to interact with the Experiment Server, as
`documented here
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/lab/experiments/IBoardBaseController.java>`_, but the most relevant are the following:

.. code-block:: java

    ////////////////////////////////////
    // 
    // General information
    //

    /**
     * Is the user accessing through facebook?
     */
    public boolean isFacebook();

    /**
     * What is the session id of the user? It is useful when using other type of communications, such
     * as iframes in the LabVIEW experiment.
     */
    public SessionID getSessionId();

    ////////////////////////////////////
    // 
    // Sending commands
    //

    /**
     * Send a string command, don't care about the result
     */
    public void sendCommand(String command);
    
    /**
     * Send a string command, notify me with the result
     */
    public void sendCommand(String command, IResponseCommandCallback callback);


    ////////////////////////////////////
    // 
    // Cleaning
    // 

    /**
     * Clean the experiment widgets and move to the list of experiments
     */
    public void clean();

    /**
     * Finish the experiment.
     */
    public void finish();


.. /* (this is to avoid highlight problems in vim)

So basically, what you do when implementing an experiment is to inherit from
``ExperimentBase``, override the ``start`` method to be notified when the
laboratory has been assigned, and then start showing the user interface and
interacting with the server through commands. In the ``end`` method, you usually
clean up the remaining resources (e.g., stop camera streams, cancel timers,
etc.).

However, there are some common operations, such as putting a panel in the
screen, or cleaning up the resources. For this reason, there is a utility class
which inherits from ``ExperimentBase`` called
`UIExperimentBase
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/lab/experiments/UIExperimentBase.java>`_,
which provides the following extra operations:

.. code-block:: java

    protected void putWidget(Widget widget);

    protected void addDisposableWidgets(IWlDisposableWidget widget);

So you don't need to implement the ``end`` method, and simply use these methods
to add the resources to be cleaned. In the binary experiment, you can see that
``BinaryExperiment`` (`see code
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/experiments/binary/ui/BinaryExperiment.java>`_)
inherits from this class. In that class, you may see that it simply calls to the
``putWidget`` method, providing the `panels implemented in that laboratory
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/experiments/binary/ui/>`_.
For instance, you can see the `user interface in XML
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/experiments/binary/ui/InteractivePanel.ui.xml>`_,
and the `attached Java code
<https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/experiments/binary/ui/InteractivePanel.java>`_
which manages the event handlers and calls the ``sendCommand`` method in the
``processSwitch`` method to interact with the laboratory.

Finally, going back to the class which inherits from
``IExperimentCreatorFactory``, it will have two methods, and you can copy and
paste code as most of them are very similar:

#. ``getCodeName``, which returns a unique code for that laboratory, and will
   later be used in the deployment.
#. ``createExperimentCreator``, which creates an ``ExperimentCreator`` class
   where you define the support in mobile phones (so later in mobile phones the
   user interface will show a different color), and where internally it will
   create the user interface. Note that it uses ``GWT.runAsync`` to define that
   this code will not be compiled in the same JavaScript and it will be loaded
   only once the user has clicked on this laboratory. The ``ExperimentCreator``
   has other method called ``createMobile``, used if you want to pass an
   alternative user interface for mobile devices, as done in the `logic
   laboratory
   <https://github.com/weblabdeusto/weblabdeusto/blob/master/client/src/es/deusto/weblab/client/experiments/logic/LogicCreatorFactory.java>`_.

.. code-block:: java

            @Override
            public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
                GWT.runAsync(new RunAsyncCallback() {
                    @Override
                    public void onSuccess() {
                        callback.onExperimentLoaded(new BinaryExperiment(
                                configurationRetriever,
                                boardController
                            ));
                    }

                    @Override
                    public void onFailure(Throwable e){
                        callback.onFailure(e);
                    }
                });
            }

So as to test all this code, you will need to read the next section (:ref:`remote_lab_deployment`).

JavaScript
..........

An easy way to develop an experiment is to use standard JavaScript.
Though you will not have access to certain GWT widgets that are already implemented,
and though you will have to implement most of the experiment and interface yourself,
it has certain advantages:

* It's easy. You simply develop an HTML file without any restriction. You include a JavaScript that WebLab provides to interface with the server.
* Does not have any dependency, other than a JavaScript script file.
* New experiments can be developed without needing to compile anything.
* Can easily make use of any kind of JavaScript library or framework.
* Possible to develop and test the experiments offline, without deploying a WebLab first. You can just open the HTML file in a browser.

What to develop
```````````````

In order to create a new experiment, essentially you need:

* An experiment server
* **An experiment client**

This section is, as you are probably aware, dedicated to the later (an experiment client). 
An experiment client provides the interface and client-side logic that your particular experiment
requires. It communicates with WebLab and the experiment server through a very simple API. 

A good way to start, however, is to simply create a new folder, with an empty HTML file.
You have certain freedom when choosing where to place it, but it is advisable to place it
within the "public" folder of the WebLab standard client. For instance, if your experiment is going to
control a remote lightbulb, you could create a jslightbulb.html, in the following path:

``src\es\deusto\weblab\public\lightbulb\jslightbulb.html``


The public folder is automatically exported when you deploy WebLab, so you can feel free to put any number
of HTML, JS or image files (or any kind of file, really) within it.

This HTML that you have just created is meant to be your experiment's interface. It will appear within WebLab Deusto as an iframe.
If we continue with the aforementioned example (an experiment to remotely control a lightbulb), you might want to add, for instance,
a webcam feed to your HTML (in order to see the lightbulb), and maybe some JavaScript button (to turn the lightbulb on and off).

Because it is just standard HTML, you can use any library or framework you wish to make your work easier.

As of now, however, our lightbulb experiment does not really connect to WebLab. You are hence probably wondering how to *actually* 
tell the lightbulb to turn off when the user presses your JS button. That is, how to send a command to the experiment server.

This is done through the JavaScript API, which will be explained next.

JavaScript API
``````````````

The WebLab API is relatively simple.
The basic API provides these base functions, which is all you really need:

* Sending a command.
* Sending a file.
* Receiving a time-left notification.
* Receiving an experiment-starts notification.
* Receiving an experiment-ends notification.
* Forcing the experiment to end early.

For JavaScript, this API can be found in the following place:

``src\es\deusto\weblab\public\jslib\jsweblab.js``

You can simply reference it from your HTML. For instance, if your HTML is within ``public\jslightbulb\jslightbulb.html``, you can do, within ``<head>``:

	``<script src="../jslib/weblabjs.js"></script>``

The API follows:
	
.. code-block:: javascript

	//! Sends a command to the experiment server.
    //!
    //! @param text Text of the command. 
    //! @param successHandler Callback that will receive the response for the command.
    //! Takes a single string as argument.
    //! @param errorHandler Callback that will receive the response for the command.
    //! Takes a single string as argument.
    //!
    this.sendCommand = function (text, successHandler, errorHandler) 


    //! Sets the callback that will be invoked when the experiment finishes. Generally,
    //! an experiment finishes when it runs out of allocated time, but it may also 
    //! be finished explicitly by the user or the experiment code, or by errors and
    //! and disconnections.
    //!
    this.setOnEndCallback = function (onEndCallback) 

    //! Sets the callbacks that will be invoked by default when a sendfile request
    //! finishes. The appropriate callback specified here will be invoked if no 
    //! callback was specified in the sendFile call, or if the sendFile was done
    //! from GWT itself and not through this API.
    //!
    //! @param onSuccess Callback invoked when the sendFile request succeeds. Takes
    //! the return message as argument.
    //! @param onError Callback invoked when the sendFile request fails. Takes the
    //! return message as argument.
    this.setFileHandlerCallbacks = function (onSuccess, onError) 

    //! Sets the startInteractionCallback. This is the callback that will be invoked
    //! after the Weblab experiment is successfully reserved, and the user can start
    //! interacting with the experiment. 
    this.setOnStartInteractionCallback = function (onStartInteractionCallback) 
	
    //! Sets the setTime callback. This is the callback that Weblab invokes when it defines
    //! the time that the experiment has left. Currently, the Weblab system only invokes
    //! this once, on startup. Hence, from the moment setTime is invoked, the experiment
    //! can take for granted that that is indeed the time it has left. Unless, of course,
    //! the experiment itself chooses to finish, or the user finishes early.
    //!
    //! @param onTimeCallback The callback to invoke when Weblab sets the time left for 
    //! the experiment.
    //!
    this.setOnTimeCallback = function (onTimeCallback) 

    //! Sets the three Weblab callbacks at once.
    //! 
    //! @param onStartInteraction Start Interaction callback.
    //! @param onTime On Time callback.
    //! @param onEnd On End callback.
    //! 
    //! @see setOnStartInteraction
    //! @see setOnTimeCallback
    //! @see setOnEndCallback
    this.setCallbacks = function (onStartInteraction, onTime, onEnd) 

    //! Retrieves a configuration property.
    //!
    //! @param name Name of the property.
    this.getProperty = function (name) 
	
    //! Retrieves a configuration property.
    //!
    //! @param name Name of the property.
    //! @param def Default value to return if the configuration property
    //! is not found.
    this.getPropertyDef = function (name, def) 

    //! Retrieves an integer configuration property.
    //!
    //! @param name Name of the property.
    this.getIntProperty = function (name) 

    //! Retrieves an integer configuration property.
    //!
    //! @param name Name of the property.
    //! @param def Default value to return if the configuration property
    //! is not found.
    this.getIntPropertyDef = function (name, def) 

    //! Finishes the experiment.
    //!
    this.clean = function () 

    //! Returns true if the experiment is active, false otherwise.
    //! An experiment is active if it has started and not finished.
    //! That is, if the server, supposedly, should be able to receive
    //! commands.
    //!
    this.isExperimentActive = function () 
	
    //! Checks whether this interface is actually connected to the real
    //! WebLab client. 
    //!
    //! @return True, if connected to the real WL client. False otherwise.
    this.checkOnline = function () 
	
    //! This method is for debugging purposes. When the WeblabJS interface is used stand-alone,
    //! offline from the real Weblab client, then the response to SendCommand will be as specified.
    //!
    //! @param response Text in the response.
    //! @param result If true, SendCommand will invoke the success handler.
    //! @param result If false, SendCommand will invoke the failure handler.
    this.dbgSetOfflineSendCommandResponse = function (response, result) 
	
	
Using the API is easy. Once the script has been included, you can simply:

.. code-block:: javascript
	
	Weblab.sendCommand( "LIGHTBULB ON", 
		function(response) {
			console.log("Light turned on successfully");
		},
		function(response) {
			console.error("Light failed to turn on");
		}
	);
	
Note that as you can see above, there are some functions that start with "dbg". Those are for development purposes.
Sometimes, for instance, it is convenient to be able to run your HTML interface stand-alone. In order for the experiment
to behave in a way that more closely resembles in its intended way, you can use these to simulate command responses
from the server and the like.


Java applets
............

You can develop the client side using Java Applets. They will not work in
tablets (iPad, Android) neither in mobile phones, and many web browsers nowadays
do not support Java applets. For this reason, it is recommended to avoid it and
rely on JavaScript or Google Web Toolkit (see below).

However, if you are going to reuse code or you need to use Java Applets for
other reasons, WebLab-Deusto supports it. If you go to
`experiments/managed/libs/client
<https://github.com/weblabdeusto/weblabdeusto/tree/master/experiments/managed/libs/client/java>`_,
you will find the Java applets source code. It is an `Eclipse
<http://www.eclipse.org/>`_ project, so you should be able to import it if you
are using this IDE. Otherwise, you can use `ant <http://ant.apache.org/>`_ to
compile it, by running::

   $ ant package

The package hierarchy is the following::

   + es.deusto.weblab.client.experiment.plugins
     + es.deusto.weblab.javadummy
       + commands
         - PulseCommand
       - JavaDummyApplet
     + java
       - WebLabApplet
       - ICommandCallback
       - ResponseCommand
       - ConfigurationManager
       - BoardController
       - Command

The ``java`` package is the library itself, used by WebLab-Deusto. The
``es.deusto.weblab.javadummy`` package is just an example of a user interface
built using this library. You may remove it and use your own package, even
outside (e.g., ``edu.myuniversity.mylab``). However, you must include the
``java`` package.

The first step is to make a class which inherits from ``WebLabApplet`` (`view
code
<https://github.com/weblabdeusto/weblabdeusto/blob/master/experiments/managed/libs/client/java/src/es/deusto/weblab/client/experiment/plugins/java/WebLabApplet.java>`_). In the
example, this class is ``JavaDummyApplet`` (`view applet code
<https://github.com/weblabdeusto/weblabdeusto/blob/master/experiments/managed/libs/client/java/src/es/deusto/weblab/client/experiment/plugins/es/deusto/weblab/javadummy/JavaDummyApplet.java>`_).
This new class is the one which will be instanciated by WebLab-Deusto. It will
be instanciated whenever the user selects the laboratory, before 
reserving it. Then, there are three methods that should be implemented by this
class:


.. code-block:: java

    public void startInteraction() {
        // When this method is called, student has access to 
        // the remote equipment (he has been assigned). You
        // can show a cool user interface for your remote 
        // laboratory and call the sendCommand methods (later
        // explained).
    }

    public void setTime(int time) {
        // This method is called to inform you how many seconds
        // the user will be using this laboratory. You should 
        // print it somewhere and maintain a custom counter.
    }

    public void end() {
        // When this method is called, the user has stated that
        // he is not using the laboratory anymore, or the system
        // has kicked him out (e.g., because his slot finished).
    }   

From this point, the client knows when the user interfaces should be loaded. So
as to interact with the Experiment server, the ``WebLabApplet`` provides a
method which gives access to the ``BoardController``. The ``BoardController``
provides a set of methods for submitting commands.

.. code-block:: java

    // From the class which inherits from JavaDummyApplet:
    MyCommandCallback callback = new MyCommandCallback();

    // Send a message to the Experiment server, and provide a callback
    // which will be called when the method comes back.
    this.getBoardController().sendCommand("turn switch on", callback);
    
The callback itself can be defined as follows: 

.. code-block:: java

    // Somewhere else
    public class MyCommandCallback inherits ICommandCallback {

        public void onSuccess(ResponseCommand response) {
            String responseText = response.getCommandString();
            // Do something with the message returned from the
            // Experiment server.
        }

        public void onFailure(String message) {
            // Something failed in the server side or in the
            // communications. Do something with the error.
        }
    }

Additionally, the ``WebLabApplet`` class provides other methods, such as:

.. code-block:: java

    // Call this if you want to terminate the current session
    this.getBoardController().onClean();

    // Retrieve String properties from the configuration.js file
    this.getConfigurationManager().getProperty("my.property", "default value");

    // Retrieve int properties from the configuration.js file
    this.getConfigurationManager().getIntProperty("my.property");

From this point, you will need to register the client in the client
configuration file. Find out how :ref:`in the following section
<remote_lab_deployment>`.

Flash applets
.............

We provide a .fla project in ``experiments/managed/libs/client/flash`` to see a
simple sample of !WebLab accessed from Adobe Flash, as well as a .as file with
all the glue code that the experiment developer might use. You can see it `in
github
<https://github.com/weblabdeusto/weblabdeusto/tree/master/experiments/managed/libs/client/flash>`_.

In order to create a new experiment using ``WeblabFlash``,
``weblab.util.WeblabFlash`` must be imported.

Done this, it is possible to access the singleton instance of ``WeblabFlash``
through its static method ``getInstance()``.

.. code-block:: actionscript

        //! Retrieves a reference to the only instance of WeblabFlash.
        //!
        public static function getInstance() : WeblabFlash {
            // ...
        }


After getting a reference to this instance the programmer should register the
weblab callbacks. This is done through the registerCallbacks method. The
callback functions to call whenever events take place are passed to
registerCallbacks as parameters. If being notified of a certain event is not
required, it is possible to pass null for it instead. Events are, in order:
``onSetTime``, ``onStartInteraction``, ``onEnd``, ``onSecondEllapsed``. This
last one is null by default and hence may not be passed at all.

.. code-block:: actionscript

    //! Registers the JS callbacks setTime, startInteraction and end, so that
    //! the appropiate user-specified delegate is automatically called when appropiate.
    //! Optionally registers a seconds timer.
    //!
    //! @param setTime Function called to set the time.
    //! @param startInteraction Function called to start interacting with the user.
    //! @param end Function called when the experiment ends.
    //! @param onSecondEllapsed Function called every second.
    public function registerCallbacks(setTime : Function, startInteraction : Function, end : Function, onSecondEllapsed : Function = null) : void{
       //...
    }

Anyway, the developer can ask for the state at any moment. An experiment may be found in one of three different states:

* ``WeblabFlash.STATE_WAITING``: When weblab is yet to call startInteraction.
* ``WeblabFlash.STATE_INTERACTING``: When startInteraction has been called and therefore the experiment has started, and is not done yet.
* ``WeblabFlash.STATE_FINISHED``: When weblab has called ``onEnd()`` or when ``onClean()`` has been called locally.

Current state may be obtained through the getcurrentState() method.

The method sendCommand is used to send commands to the server. It takes a string with the command as first parameter plus two callback functions. First of those will be called in case the command succeeds and the other one in case it fails. Both callbacks are passed a message string when called.

.. code-block:: actionscript

        //! Sends a command to the server. Its response will be received asynchroneously through
        //! two alternative callbacks.
        //!
        //! @param command_str The command string.
        //! @param onSuccess Function to call if the command succeeds. Should take the response string
        //! as a parameter.
        //! @param onError Function to call if the command fails. Should take the response string
        //! as a paramter.
        public function sendCommand(command_str : String, onSuccess : Function, onError : Function) {
           //...
        }

The time of an experiment is limited. ``WeblabFlash`` internally keeps a timer. This timer is
initialized to the value passed by weblab through its ``setTime()`` call and
starts decreasing once interaction starts. When zero is reached, ``onClean()``
is automatically called and the experiment is considered to be finished.
``onClean()`` may also be called explicitally before the timer reaches zero.
Moreover, weblab may call ``onEnd()`` at any time to finish the experiment.
Whenever this happens, the programmer is responsible to clean all resources in
use (such as timers).

In order to retrieve the global configuration values, stored in the
configuration.xml file in the client side, the developer may call these methods:

.. code-block:: actionscript

        //! Retrieves a property as a string.
        //!
        //! @param prop The name of the property.
        //! @param def The default value to return if the property is not found.
        public function getPropertyDef( prop : String, def : String):String {
            // ...
        }

        //! Retrieves a property as a string.
        //!
        //! @param prop The name of the property.
        public function getProperty( prop : String ):String {
            // ...
        }

        //! Retrieves an integer property.
        //!
        //! @param prop The name of the property.
        //! @param def The default value to return if the property is not found.
        public function getIntPropertyDef( prop : String, def : int ):int {
            // ...
        }

        //! Retrieves an integer property.
        //!
        //! @param prop The name of the property.
        public function getIntProperty( prop : String ):int {
            // ...
        }

From this point, you will need to register the client in the client
configuration file. Find out how :ref:`in the following section
<remote_lab_deployment>`.


.. _managed_libraries_server:

Server side
^^^^^^^^^^^

This section covers how to develop the server side of a remote laboratory using the WebLab-Deusto Managed model.

Introduction
............

There are two ways to develop a remote laboratory using the WebLab-Deusto API in the managed model:

* Using Python (which is the programming language used by the rest of the
  WebLab-Deusto system) as a native laboratory (therefore managing even the
  configuration through WebLab-Deusto).
* Running an external process which acts as a XML-RPC server. We provide
  libraries for doing this automatically, described below.

In this case, there is no prefered way to develop the laboratories, whatever is
easier for the developer.

All the libraries can be found in the repository, in the
`experiments/managed/libs/server
<https://github.com/weblabdeusto/weblabdeusto/tree/master/experiments/managed/libs/server>`_
directory.


Server APIs
...........

Before starting, there is a concept of API version or level for the Experiment
server API. Basically, we started with a very simple API which contained the
following methods::

    void startExperiment();
    void dispose();
    String sendCommand(String);
    String sendFile(String content, String fileInfo);

Changing this API breaks compatibility with existing laboratories. For this
reason, we implemented a method called ``get_api``, which returns the current
API. And at the moment of this writing, there are 3 APIs:

* ``1``, which is the one presented above.
* ``2``, which is the one used in the majority of our laboratories, but not in
  all the libraries at this moment.
* ``2_concurrent``, which right now is only provided in Python, while it should
  be easy to change the underlying XML-RPC services in each library to support
  it.

The Laboratory server can define which is the API of a laboratory. If it is not
stated by the Laboratory server, the system attempts to request the API version.
If it fails to provide it, it will assume that it is version ``1`` (where there
was no such concept, and therefore, no explicit method detailing it). From that
point, it will know which version the Experiment server is running and it will
call the methods in one way or other (e.g., providing arguments to the
startExperiment or not, using more methods, etc.).


WebLab-Deusto server (Python)
.............................

In the case of Python, no external library is required, other than WebLab-Deusto
itself. A dummy example would be the following:

.. code-block:: python

    import json

    from weblab.experiment.experiment import Experiment
    import weblab.experiment.level as ExperimentApiLevel

    class DummyExperiment(Experiment):
        
        def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
            super(DummyExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kwargs)
            
            # Keep an instance of the configuration manager
            self._cfg_manager = cfg_manager

            # Retrieve a configuration variable from the configuration file:
            self._cfg_manager.get_value("property_name", "default_value") 

        def do_start_experiment(self, client_initial_data, server_initial_data):
            """A new student is granted access to the laboratory (scheduled,
            authenticated, etc.)"""

            # Data provided by the client
            print "Client initial data:", json.loads(client_initial_data)
            # Data provided by the server (username, time slot...)
            print "Server initial data:", json.loads(server_initial_data)

            # Default response
            return "{}"

            # If you want to provide some initial data (URLs to cameras or so)
            # return json.dumps({ "initial_configuration" : "this will be batch", "batch" : False })

            # In case of batch laboratories, use the following:
            # return json.dumps({ "initial_configuration" : "this will be batch", "batch" : True })

        def do_get_api(self):
            # The current Laboratory API is the version 2. Whenever we add new
            # methods or change the API, it will not affect you if you are
            # stating that the API that the rest of the system must use with
            # this experiment is v2.
            return ExperimentApiLevel.level_2 

        def do_dispose(self):
            """ The user exited (or the time slot finished). Clean resources. """

            print "User left"

            return "{}"

        def do_send_file_to_device(self, file_content, file_info):
            """ A file, encoded in BASE64, has been sent. Do something with it """

            return "A response that the client will receive"

        def do_send_command_to_device(self, command):
            """ A command has been submitted. Do something with it and reply. """

            print "Command received:", command

            return "Got your command"

        def do_should_finish(self):
            """
            Should the experiment finish? If the experiment server should be able to
            say "I've finished", it will be asked every few time; if the experiment
            is completely interactive (so it's up to the user and the permissions of
            the user to say when the session should finish), it will never be asked.

            Therefore, this method will return a numeric result, being:
              - result > 0: it hasn't finished but ask within result seconds.
              - result == 0: completely interactive, don't ask again
              - result < 0: it has finished.
            """
            return 0


.. ** (to avoid problems with highlighting in Python)

From this point, you can now deploy the experiment, as explained in the
:ref:`following section <remote_lab_deployment>`.

However, it is worth mentioning that there is other API called the concurrent
API, which enables that the Experiment server manages multiple concurrent users
at the same time. For example, imagine that you want that a fixed number (e.g.,
10) students talk each other while using the laboratory. You can change this in
the deployment, as it is later explained in
:ref:`remote_lab_deployment_concurrency`. But then, you would not be able to
differentiate who is accessing, or send different messages to each student. For
this reason, the concurrent API provides a unique identifier (which is a random
number, and is not maintained across sessions) called ``session_id``. This
``session_id`` is passed through all the methods, as seen below:

.. code-block:: python

    from weblab.experiment.concurrent_experiment import ConcurrentExperiment
    import weblab.experiment.level as ExperimentApiLevel

    class DummyConcurrentExperiment(ConcurrentExperiment):
        
        def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
            super(DummyConcurrentExperiment,self).__init__(coord_address, locator, cfg_manager, *args, **kwargs)
            
            # Keep an instance of the configuration manager
            self._cfg_manager = cfg_manager

            # Retrieve a configuration variable from the configuration file:
            self._cfg_manager.get_value("property_name", "default_value") 

        def do_start_experiment(self, session_id, client_initial_data, server_initial_data):
            # Store in a local dictionary that there is a new user defined as
            # session_id

            return "{}"

        def do_get_api(self):
            return ExperimentApiLevel.level_2_concurrent

        def do_dispose(self, session_id):
            # Remove that particular user from the active users
            return "{}"

        def do_send_file_to_device(self, session_id, file_content, file_info):
            # That user (identified by session_id) is sending a file

            return "A response that the client will receive"

        def do_send_command_to_device(self, session_id, command):
            # That user (identified by session_id) is sending a command

            print "Command received:", command

            return "Got your command"

        def do_should_finish(self, session_id):
            # Should that user be kicked out?
            return 0

.. ** (to avoid problems with highlighting in vim)


Java
....

The Java library can be found in the `experiments/managed/libs/server/java
<https://github.com/weblabdeusto/weblabdeusto/tree/master/experiments/managed/libs/server/java>`_
library. It is an `Eclipse <http://www.eclipse.org/>`_ project, so you should be
able to import it if you are using this IDE. Otherwise, you can use `ant
<http://ant.apache.org/>`_ to compile it, by running::

   $ ant build 
   $ ant run

The structure of the source code is the following::

   + src
     + es/deusto/weblab/experimentservers
       + exceptions
         - (defined exceptions)
       - ExperimentServer.java
       - Launcher.java
       - (Other auxiliar classes)
     + com/example/weblab
       - DummyExperimentServerMain.java
       - DummyExperimentServer.java

There, the important classes are those available in the package ``es.deusto``.
The ones in the ``com.example`` can be removed and replaced by the proper
package of your application. They are there as a working example of what the
interface is.

The two important classes are ``ExperimentServer`` and ``Launcher``. The former
is a class which defines all the optional methods which can be implemented by
the experiment developer (e.g., a method for receiving commands). The latter is a
class that will start a XML-RPC server taking an instance of the class generated
by the experiment developer.

The first thing you must implement is a class which inherits from
``ExperimentServer``. An example of this is the ``DummyExperimentServer`` class,
which supports multiple methods such as:

.. code-block:: java

    // A new user comes in
    public String startExperiment(String clientInitialData, String serverInitialData) throws WebLabException {
        System.out.println("I'm at startExperiment");
        System.out.println("The client provided me this data: " + clientInitialData);
        System.out.println("The server provided me this data: " + serverInitialData);
        return "{}";
    }

    // Typical server initial data:
    // [java] The server provided me this data: 
    //        {
    //          "request.locale": "es", 
    //          "request.experiment_id.experiment_name": "dummy", 
    //          "request.experiment_id.category_name": "Dummy experiments", 
    //          "priority.queue.slot.initialization_in_accounting": true, 
    //          "priority.queue.slot.start": "2013-03-27 00:36:08.397675", 
    //          "priority.queue.slot.length": "200", 
    //          "request.username": "admin" 
    //        }

    // A user leaves (or is kicked out)
    public String dispose() {
        System.out.println("I'm at dispose");
        return "ok";
    }

    public String sendFile(File file, String fileInfo)  throws WebLabException {
        System.out.println("I'm at send_program: " + file.getAbsolutePath() + "; fileInfo: " + fileInfo);
        return "ok";
    }

    public String sendCommand(String command)  throws WebLabException {
        System.out.println("I'm at send_command: " + command);
        return "ok";
    }

Those methods should parse the command send by the client and do the required
actions (such as interact with certain equipment and return some response).

Once you have implemented this class, you can use the ``Launcher`` as:

.. code-block:: java

    public class DummyExperimentServerMain {
        public static void main(String [] args) throws Exception{
            int port = 10039;
            IExperimentServer experimentServer = new DummyExperimentServer();
            Launcher launcher = new Launcher(port, experimentServer);
            launcher.start();
        }
    }

This way, you willhave the experiment running on port ``10039`` in this case.
Once you have the server running, you will need to register it in WebLab-Deusto.
This is explained in :ref:`this section <remote_lab_deployment>`.

.NET
....

.. note::

   To be written (April 2013).


C
..

.. note::

   To be written (April 2013).


C++
...

.. note::

   To be written (April 2013).


Node.js
.......

.. note::

   To be written (April 2013).


.. _managed_library_server_labview:

LabVIEW
.......

.. note::

   To be written (April 2013).

Python
......

The Python library can be found in the `experiments/managed/libs/server/python
<https://github.com/weblabdeusto/weblabdeusto/tree/master/experiments/managed/libs/server/python>`_.
It does not rely on any external library, since Python comes with an XML-RPC
server included. You will find two modules:

* ``weblab_server.py``, which includes the ``ExperimentServer`` and the
  ``Launcher``.
* ``sample.py``, which includes an example of how to use the
  ``ExperimentServer`` code, and how to run it with the ``Launcher``.

Basically, you have to create a class which inherits from ``ExperimentServer``
and implements a subset of the following methods (none of these are required 
since they are already implemented in the parent class):

.. code-block:: python

    from weblab_server import ExperimentServer, Launcher

    class DummyExperimentServer(ExperimentServer):

        def start_experiment(self, client_initial_data, server_initial_data):
            print "start_experiment", client_initial_data, server_initial_data
            return "{}"

        def get_api(self):
            return "2"

        def send_file(self, content, file_info):
            print "send_file", file_info
            return "ok"

        def send_command(self, command_string):
            print "send_command", command_string
            return "ok"

        def dispose(self):
            print "dispose"
            return "{}"

        def should_finish(self):
            return 0

Then, you only need to create a Launcher with a port, and start it:

.. code-block:: python

    launcher = Launcher(12345, DummyExperimentServer())
    launcher.start()



Tools
^^^^^

The :ref:`Experiment Server Tester <experiment_server_tester>` helps you in the
process of writing the server code, by being able to test it easily with a
graphic tool, and even create your own scripts to verify that it works as
expected. Refer to that documentation for using it.

.. image:: /_static/screenshots/weblab_experiment_server_tester.png
   :width: 700 px
   :align: center


Unmanaged laboratories
----------------------

At this moment, we are only documenting the unmanaged laboratories with
Virtual Machines.

Virtual machines
^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   deploying_vm_experiment

Summary
-------

With this section, you have learnt to develop a new remote laboratory using
WebLab-Deusto. Now it's time to deploy it, going to :ref:`the following section
<remote_lab_deployment>`.

