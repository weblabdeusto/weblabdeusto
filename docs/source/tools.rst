Tools
=====

WebLab Bot
----------

A Remote Laboratory is a software system that requires a complex workflow and that will require to face big load of users in certain moments. There are different constraints that have an impact on the latency and performance of WebLab-Deusto:
* Deployment configuration: only one server, multiple servers, storing sessions in database or in memory...
* Deployed system: what machine, operating system, Python or MySQL versions...
* Tens or hundreds of students being queued
* Tens or hundreds of students using experiments

In order to test these variables easily, a students simulator has been implemented, and it is called WebLab Bot. The WebLab Bot tool is used for three purposes:
* Measure the time with each configuration
* Perform stress tests of the system, finding the errors created when developing new features
* Test the system in new operating systems or software versions

.. image:: /_static/bot_sample.png
   :width: 400 px
   :align: center

**TO BE WRITTEN** The old documentation is available `here <http://code.google.com/p/weblabdeusto/wiki/Latest_WebLabBot>`_, but needs to be updated.

