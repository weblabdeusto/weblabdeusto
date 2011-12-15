In this sample, the communication with an experiment ("ud-dummy") is through XML-RPC using an external port (10039).

It's useful for two things:

 a) To measure the impact of XML-RPC protocol instead of Direct. In order to test this, run the launch_sample_xmlrpc_machine.py script to launch both servers (the core servers and the experiment server).

 b) To test a particular experiment or library implemented with the provided libraries. In order to test this, run the launch_sample_xmlrpc.py script to launch only the core servers, and then run your experiment listening in the 10039 port.

In any case, once logged in, use the ud-dummy experiment to see the xmlrpc in action.

