Sample laboratories
===================

FPGA
----

`ud-fpga
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=FPGA%20experiments&exp.name=ud-demo-fpga>`_
lets you remotely practise with a Field Programmable Gate Array. Through the
Xilinx software, you can write a FPGA program locally as you normally would.
Once the program is compiled, and ready to be tested, you should simply upload
the binary ".bit" file through the experiment.

ud-fpga will automatically program the FPGA board with the binary you provided, and start running it. To see the results, a Webcam is of course provided. You may also interact with the board remotely, by using the provided widgets. Though the widgets themselves might appear artificial, they will send a signal to the board just like their physical counterparts would.

However, due to certain safety concerns, in the demo version you can't upload your own file for this demo. Instead, a specific demo program (which has already been uploaded) will be used. Everything else will work as in the standard FPGA experiment.

Aquarium
--------

**TO BE WRITTEN**

Robot
-----

**TO BE WRITTEN**

VISIR
-----

The `VISIR experiment <https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=VISIR%20experiments&exp.name=visir>`_
lets you access the `BTH OpenLabs VISIR <http://openlabs.bth.se/electronics>`_
through WebLab-Deusto.

BTH OpenLabs VISIR (Virtual Instrument Systems In Reality) is a Remote
Laboratory developed in the `Blekinge Institute of Technology
<http://www.bth.se>`_, which supports remote experimentation with real
electronic circuits.

Students create circuits using the web interface, such as the following (where
two resistors, of 10k and 1k are placed in serial and connected to the Digital
MultiMeter):

.. image:: /_static/example_logic.png
   :align: center

And as a result of this, the digital multimeter will show the sum of the two
resistors:

.. image:: /_static/visir_result.png
   :align: center

This is possible given that VISIR uses a switching matrix, where all the
resistors and other components are located, and with a set of relays it creates
the circuit requested by the student:

.. image:: /_static/visir_switching_matrix.png
   :align: center

Furthermore, multiple students can access VISIR and take different measurements
at the very same time. VISIR will create each circuit and take the measurement
each time.

There is more information in the website of the `VISIR project
<http://openlabs.bth.se/electronics>`_ or in `related
papers <http://scholar.google.es/scholar?q=visir+electronics>`_.


ud-logic
--------

`ud-logic <https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=PIC%20experiments&exp.name=ud-logic>`_
is a rather simple game implemented as an experiment. It is mainly for
demonstration purposes. Players are presented with a circuit diagram made up of
6 connected logic gates. Five of these gates show the type of gate: AND, NAND,
OR, NOR or XOR. The symbols, as described in `the wikipedia
<http://en.wikipedia.org/wiki/Logic_gate#Symbols>`_, are the following:

.. |AND| image:: /_static/logic/small_AND.png

.. |OR| image:: /_static/logic/small_OR.png

.. |XOR| image:: /_static/logic/small_XOR.png

.. |NAND| image:: /_static/logic/small_NAND.png

.. |NOR| image:: /_static/logic/small_NOR.png

=====  ======
Name   Image
=====  ======
AND    |AND|
OR     |OR|
XOR    |XOR|
NAND   |NAND|
NOR    |NOR|
=====  ======

Players must choose the type of the sixth gate so the result of the circuit is
1. Sometimes, several types might yield the desired result, and they will all be
considered correct.

When the players succeed, they are awarded one point and a new diagram is
generated and they may choose a gate again. The process continues until the time
expires or a wrong gate is chosen. When the process finishes, players can see
their position in the ranking linked. The more points they get in the provided
time, the higher they rank.

This experiment, for demonstration purposes, is usually connected to a hardware
board, which can be seen through the provided Webcam stream. Thus, notice that
whenever the gate choice is right, a message will appear in the board’s screen,
and the LEDs of the board will lit.

.. image:: /_static/example_logic.png
   :width: 500 px
   :align: center

In the example above, in red it is written what the results will be, regardless
the value of the unknown gate. For instance, in the upper level, **1 NOR 0** is
**0** (**1 OR 0** is **1**, and **not 1** is **0**). When solving the whole
circuit, it is clear that the final output, which must be **1**, is the result
of **? AND 1**, being **?** the result of the unknown gate.

Therefore, we need to have **1** as output of the unknown gate. So the question is:
which gate has **0** and **0** as inputs and **1** as output? **AND, OR** and
**XOR** fail to do this, so the solutions in this case are **NOR** or **NAND**.
