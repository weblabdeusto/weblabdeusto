.. _tools:

Tools
=====

.. contents:: Table of Contents

.. _bot:

WebLab Bot
----------

A Remote Laboratory is a software system that requires a complex workflow and
that will require to face big load of users in certain moments. There are
different constraints that have an impact on the latency and performance of
WebLab-Deusto:

* Deployment configuration: only one server, multiple servers, storing sessions in database or in memory...
* Deployed system: what machine, operating system, Python or MySQL versions...
* Tens or hundreds of students being queued
* Tens or hundreds of students using experiments

In order to test these variables easily, a students simulator has been
implemented, and it is called WebLab Bot. The WebLab Bot tool is used for three
purposes:

* Measure the time with each configuration
* Perform stress tests of the system, finding the errors created when developing new features
* Test the system in new operating systems or software versions

.. image:: /_static/bot_sample.png
   :width: 400 px
   :align: center

So as to run it, you need a configuration file, such as the one available in
`tools/Bot/configuration.py.dist
<https://github.com/weblabdeusto/weblabdeusto/tree/master/tools/Bot/configuration.py.dist>`_.
Copy it to ``configuration.py`` and change the required variables (e.g., change
the credentials, URLs, etc.). The ``consumer/run.py`` referes to the ``run.py``
file generated whenever you created an environment, such as::

    $ weblab-admin create consumer

The number of iterations define how many times the same scenario will be
repeated. The number of concurrent users is defined in the generate_scenarios
method, in the different two ``for`` loops. You may add other loops or change
these, but the idea is that in this example, it will be tested with 1 student,
2, 3, 4, 5, 10, 15, 20, 25 ..., 140, 145 and 150::

    for protocol in cfg_util.get_supported_protocols():
        for number in range(1, 5):
            scenarios.append(
                    Scenario(
                        cfg_util.new_bot_users(number, new_standard_bot_user, 0, STEP_DELAY, protocol),
                        protocol, number
                    )
                )

        for number in range(5, 151, 5):
            scenarios.append(
                    Scenario(
                        cfg_util.new_bot_users(number, new_standard_bot_user, STEP_DELAY * (5 -1), STEP_DELAY, protocol),
                        protocol, number
                    )
                )

Additionally, you need to install `matplotlib <http://matplotlib.org/>`_::

    # (in Ubuntu, the following requires some packages, such as build-essential, libfreetype6-dev or libpng-dev)
    pip install matplotlib

Then, simply call::

   weblab-bot.py

This will start the WebLab-Deusto instance, run the proposed scenario, and then
stop it, for each iteration and scenario defined. Running it will generate the
following output::

    ********************
    CONFIGURATION consumer/run.py
    Unique id: D_2013_03_31_T_11_38_17_
    ********************

    New trial. 1 iterations
     iteration 0 .  {'route1': 1} [ 0 exceptions ] 
    Cleaning results... Sun Mar 31 11:38:28 2013
    Storing results... Sun Mar 31 11:38:28 2013
    Results stored Sun Mar 31 11:38:28 2013
       -> Scenario: <Scenario category="JSON" identifier="1" />
       -> Results stored in logs/botclient_D_2013_03_31_T_11_38_17__SCEN_0_CONFIG_0.pickle
       -> Serializing results...
       -> Done

    [...]

    New trial. 1 iterations
     iteration 0 ....  {'route1': 4} [ 0 exceptions ] 
    Cleaning results... Sun Mar 31 11:39:19 2013
    Storing results... Sun Mar 31 11:39:19 2013
    Results stored Sun Mar 31 11:39:19 2013
       -> Scenario: <Scenario category="JSON" identifier="4" />
       -> Results stored in logs/botclient_D_2013_03_31_T_11_38_17__SCEN_3_CONFIG_0.pickle
       -> Serializing results...
       -> Done
    Writing results to file raw_information_D_2013_03_31_T_11_38_17_.dump... 2013-03-31 11:39:19.866922
    Generating graphics...
    Executing figures/generate_figures_D_2013_03_31_T_11_38_17_.py... [done]
    HTML file available in botclient_D_2013_03_31_T_11_38_17_.html
    Finished plotting; Sun Mar 31 11:39:31 2013, 251 millis
    Done 2013-03-31 11:39:31.251789

The HTML file that it points out contains all the graphics for each method.

If you don't want to start the process each time (e.g., you want to test it with
an existing WebLab-Deusto instance that you don't want to stop), then, pass the
following argument::

   weblab-bot.py --dont-start-processes

As in the case of ``weblab-admin``, in UNIX systems you may also use
``weblab-bot`` (instead of ``weblab-bot.py``).

.. _experiment_server_tester:

Experiment Server Tester
------------------------

.. warning::

   **THIS TOOL NEEDS TO BE UPGRADED TO SUPPORT THE NEW APIs**

In order to make it easy to test the experiment server under development,
WebLab-Deusto provides a tool called ExperimentServerTester (available in
`tools/ExperimentServerTester
<https://github.com/weblabdeusto/weblabdeusto/tree/master/tools/ExperimentServerTester>`_). This is a Python application (requires
both Python 2.6 and `wxPython <http://www.wxpython.org/download.php#stable>`_,
both available for GNU/Linux, Microsoft Windows and Mac OS X) that makes it easy
to interact with the server as WebLab-Deusto would do it. You can use the
provided assistant (pressing on "Send command" will send the command you have
written):

.. image:: /_static/screenshots/weblab_experiment_server_tester.png
   :width: 700 px
   :align: center


Or you can make a script. This could be a full example of the provided API (in
addition to all the Python API):

.. code-block:: python

    connect("127.0.0.1", "10039", "/weblab")
    test_me("hello")

    start_experiment()
    send_file("script.py", "A script file")
    send_command("Test Command")
    msg_box("Test Message", "test")
    dispose()

    disconnect()

.. image:: /_static/screenshots/weblab_experiment_server_tester_script.png
   :width: 700 px
   :align: center

While this tool is still in an experimental status, it can already help the
development of experiments.

.. _visir_battle_tester:

VISIR Battle Tester
-------------------

The VISIR Battle Tester (available in `tools/VisirBattleTester
<https://github.com/weblabdeusto/weblabdeusto/tree/master/tools/VisirBattleTester>`_
is an automated tool to evaluate the performance of WebLab-Deusto with VISIR. It simulates
multiple concurrent students interacting with a VISIR in a WebLab-Deusto system,
testing different measurements and validating that the results are the
expected, in certain range.

For example, it may send a command which is a request that it knows that it
should return 900, and checks that there is up to a 20% of error margin:

.. code-block:: python

    before = time.time()
    response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_900 % visir_sessionid))
    after = time.time()
    result = visir_commands.parse_command_response(response)
    ar3 = AssertionResult(900.0, 900.0 * 0.2, result)
    if DEBUG and ar3.failed:
        print "[Failed at 3rd]" + str(ar3)
    if not IGNORE_ASSERTIONS:
        assertions.append(ar3)
    times.append(after - before)

So as to run it, change the credentials and URL in the ``run.py`` file and run
it.

