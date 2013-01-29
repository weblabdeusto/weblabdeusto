.. _external_tools_federation:

External tools integration through federation
=============================================

The easiest way to make it work from external tools is using the federation API.
We currently provide APIs for various programming languages (`.NET
<https://github.com/weblabdeusto/weblabdeusto/tree/master/server/consumers/dotnet>`_,
`PHP
<https://github.com/weblabdeusto/weblabdeusto/tree/master/server/consumers/php>`_, `Python <https://github.com/weblabdeusto/weblabdeusto/blob/master/server/src/weblab/core/coordinator/clients/weblabdeusto.py>`_),
and there are external efforts for other languages (`Ruby
<https://github.com/lms4labs/deustorb>`_). 

Background
----------

As described in the :ref:`federation section <federation>`, WebLab-Deusto
supports federation. This means that two WebLab-Deusto systems can exchange
remote labs without dealing with particular users, as seen in the following
figure:

.. image:: /_static/federation_external_step1.png
   :width: 700 px
   :align: center

This basically means that in the example, the system deployed in ``University
A`` manages authentication and authorization, so its the one who knows who are
the users, etc. The contract between the systems of ``University A`` and
``University B`` does not need to deal with users or groups: if ``University A``
can access three different laboratories, then it's ``University A`` who must
choose which users can access each of these laboratories.

However, this idea is essentially what is aimed when integrating a remote
laboratory in a Learning or Content Management System (LMS/CMS). It is the LMS
the one that chooses what authentication mechanisms must be used, what students
are in which courses, and which courses should use which laboratories.

Therefore, using the federation APIs enable this second scheme, where the
LMS/CMS is basically a WebLab-Deusto consumer, and uses the same federation
protocol that other LMS/CMS use:

.. image:: /_static/federation_external_step2.png
   :width: 700 px
   :align: center

If the federation protocol does not support transitivity (this is, a consumer
may not re-share the laboratories to a third-party consumer), the LMS/CMS would
need to be configured with each external remote laboratory, which is not an
ideal situation. Typically, remote laboratory managers are the ones who deal
with this type of contracts. However, WebLab-Deusto supports transitivity (see
the :ref:`federation section <federation>`), so it is possible to have a local
WebLab-Deusto instance, configure it in the LMS, and configure in this
WebLab-Deusto instance as many external federated instances as required.

.. image:: /_static/federation_external_step3.png
   :width: 700 px
   :align: center

How does it work?
-----------------

Let's take the example of the :ref:`.NET consumer
<https://github.com/weblabdeusto/weblabdeusto/blob/144dc83a17bf4b7b5f38589fd83ec82013f13661/server/consumers/dotnet/Sample.cs>`.
It provides a set of data classes, but the main class is `WebLabDeustoClient`.
Once you create an instance of it, you can create a session by passing custom
credentials::

            WebLabDeustoClient weblab = new WebLabDeustoClient("http://localhost/weblab/");

            SessionId sessionId = weblab.Login("user", "password");

And you can use this session identifier to retrieve the list of available
laboratories::

            foreach(ExperimentPermission permission in weblab.ListExperiments(sessionId))
                Console.WriteLine("I have permission to use {0} of category {1} during {2} seconds", permission.Name, permission.Category, permission.AssignedTime); 

Which will print in the console something like::

            I have permission to use ud-logic of the category PIC experiments during 150 seconds
            I have permission to use submarine of the category Aquatic experiments during 150 seconds
            [...]

In addition, and more importantly, you can use the session identifier to perform
a reservation. For instance, if you want to create a reservation of the
``ud-logic`` laboratory, you can provide the following the laboratory and the
category::

            Reservation reservation = weblab.ReserveExperiment(sessionId, "ud-logic", "PIC experiments", consumerData);

Now, the fourth argument is ``consumerData``, which represents additional
information that the consumer system (e.g. a LMS) will provide. This includes
statistics information like the user-agent (i.e. what web browser is the student
using?), the referer (i.e. where did he come from?) or the IP address, but also
information about the reservation itself: who is the user, what is the maximum
time that he will have for the laboratory (e.g. the consumer may have 150
seconds, but still the consumer can restrict it to 50 seconds for a group of
students), or a certain priority::

    //            consumerData["user_agent"]    = "";
    //            consumerData["referer"]       = "";
    //            consumerData["mobile"]        = false;
    //            consumerData["facebook"]      = false;
    //            consumerData["from_ip"]       = "...";

    // 
    // Additionally, the consumerData may be used to provide scheduling arguments,
    // or to provide a user identifier (that could be an anonymized hash).
    // 
                consumerData["external_user"]                = "an_external_user_identifier";
    //            consumerData["priority"]                     = 3; // the lower, the better
    //            consumerData["time_allowed"]                 = 100; // seconds
    //            consumerData["initialization_in_accounting"] = false;

Finally, the consumer will generate a URL that can safely be forwarded to the
student. It includes a reservation identifier, which can only be used for
actions related to that reservation. For instance, the student can not use that
reservation_id to obtain the list of laboratories or create new reservations::

            Console.WriteLine(reservation);

            string url = weblab.CreateClient(reservation);

            Console.WriteLine(url);

