Sample laboratories
===================

This section presents the a set of sample laboratories available in the
University of Deusto.

.. note::

    The terms *laboratory*, *experiment* or *rig* are a common problem
    in the remote laboratories literature. We will use laboratory or 
    experiment identically in this document. But take into account that
    in the case of the CPLD there is a single laboratory but there are
    two copies (commonly called *rigs*) of them, and students are balanced
    among them. But on the Robot laboratory, there are three different
    *laboratories* running on the same single *rig*. This way, 
    WebLab-Deusto separates *resources* (*rigs*) from *laboratories*.

.. contents:: Table of Contents

FPGA
----

`ud-fpga
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=FPGA%20experiments&exp.name=ud-demo-fpga>`_
lets you remotely practise with a `Field Programmable Gate Array
<en.wikipedia.org/wiki/FPGA>`_. Through the Xilinx software, you can write a
FPGA program locally as you normally would.  Once the program is compiled, and
ready to be tested, you should simply upload the binary ".bit" file through the
experiment.

ud-fpga will automatically program the FPGA board with the binary you provided, and start running it. To see the results, a Webcam is of course provided. You may also interact with the board remotely, by using the provided widgets. Though the widgets themselves might appear artificial, they will send a signal to the board just like their physical counterparts would.

However, due to certain safety concerns, in the demo version you can't upload your own file for this demo. Instead, a specific demo program (which has already been uploaded) will be used. Everything else will work as in the standard FPGA experiment.

.. image:: /_static/weblab_box.jpg
   :align: center

The FPGA laboratory, as other WebLab-Deusto laboratories (PIC or CPLD), is
developed within the WebLab-Box. On the WebLab-Box, the device, as well as a
`fit-pc <http://www.fit-pc.com/>`_, a PIC microcontroller, a camera, lighting
system and networking materials is installed, so as to make it easier to create
and deploy new laboratories.

.. image:: /_static/WebLabBox.jpg
   :align: center

* **Target audience:** *Electronics Engineering students*.

CPLD
----

`ud-demo-pld
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=PLD%20experiments&exp.name=ud-demo-pld>`_
lets you remotely practise with a `Programmable Logic Device
<http://en.wikipedia.org/wiki/CPLD>`_.

With the standard PLD experiment, through the Xilinx software you can write a
PLD program locally as you normally would. Once the program is compiled, and
ready to be tested, you can simply upload the binary ".jed" file, and it will be
programmed on the physical board and run.

However, due to certain safety concerns, you can't upload your own file for this
demo. Instead, a specific demo program (which has already been uploaded) will be
used. Everything else will work as in the standard FPGA experiment.

That binary file will be automatically programmed into the board, and it will
start running. To see the results, a Webcam is provided. You may also interact
with the board remotely, by using the provided widgets. Though the widgets
themselves might appear artificial, they will send a signal to the board just
like their physical counterparts would.

As the FPGA, the CPLD laboratory is running in the WebLab-Box. However, two
different laboratories are available. The queue of students is balanced between
both copies, so it goes twice faster.

.. image:: /_static/demo-pld.jpg
   :align: center

* **Target audience:** *Electronics Engineering students*.
* **Video:** http://www.youtube.com/watch?v=zON7oYtssrw

Aquarium
--------
The `aquarium laboratory
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=Aquatic%20experiments&exp.name=submarine>`_
creates an access to a real aquarium located in the University of Deusto. On it,
it is possible to feed the fish, turn on and off the lights, and, if the
submarine is in the water and it is charged, control the submarine. The problem
is that most of the time, the submarine is out of battery so we only put it in
the fishtank certain days.

Regarding feeding the fish, it may seem dangerous, but it is not. The system
feeds them automatically three times a day, every 8 hour. If a user feeds them,
then it does not let any other user to feed them before the next shift,
guaranteeing that they are only fed three times. So go ahead and try it!

The initial rationale behind this laboratory is that groups of primary school
students are responsible of the life of these fish (even if they are not under a
real danger). Teachers may know which groups of students have feed them
correctly, which students didn't forget and which students coordinated correctly
so no one overfed the fish. 

However, at the time of this writing ongoing work is being done for adding more
sensors to this laboratory, so stay tuned ;-)

From a technical perspective, the whole laboratory is deployed in
http://fishtank.weblab.deusto.es/, which uses a low cost ARM microprocessor
called `IGEPv2
<http://igep.es/index.php?option=com_content&view=article&id=46&Itemid=55>`_. So
basically it is an example of :ref:`federated system <federation>`.

.. image:: /_static/submarine.jpg
   :align: center


* **Target audience:** initially, *primary school students*. Right now the focus is changing to take into account physics principles with sensors.

Robot
-----

The robot laboratory uses the commercial robot *Azkar-bot*, with an attached
microcontroller. WebLab-Deusto manages to establish that three different
learning activities are using the same equipment, so the scheduling system will
queue other users internally.

.. image:: /_static/robot.jpg
   :align: center

* **Video:** http://www.youtube.com/watch?v=1WWAZVyuOBg

robot-proglist
^^^^^^^^^^^^^^

`robot-proglist
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=Robot%20experiments&exp.name=robot-proglist>`_
lets you choose one among a few of predefined programs to program the bot with.

The programs currently available are the following:

**Follow black line**

The robot will first move randomly while avoiding obstacles (walls) until it
finds the black line. It will then position itself on the line and follow it
using its infrared sensors

**Walk alone**

Will simply walk around while avoiding any obstacles in its way.

**Interactive Demo**

Programs it with the same program that is used in the robot-movement. Doesn’t
really do much because there are no controls available in this mode.

**Turn left & turn right**

Rotates left and right, non-stop.


robot-movement
^^^^^^^^^^^^^^

`robot-movement
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=Robot%20experiments&exp.name=robot-movement>`_
lets you control a bot remotely. The bot can move forward or backward, and turn
to both sides.

To make the bot move, simply click on the appropriate button. Alternatively, you
can control the bot by using the arrows on your keyboard. Remember that the bot
will move according to its own position, and not to the position of the camera.

The bot will not obey you if it finds a wall in its way, in which case it will
try to avoid it.

.. image:: /_static/screenshots/weblab-robot.jpg
   :align: center

robot-standard
^^^^^^^^^^^^^^

`robot-standard
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=Robot%20experiments&exp.name=robot-standard>`_
lets you program the bot yourself, with any program you wish.

The bot uses a PIC processor, so the program should be written using the Xilinx
PIC compiler. It is noteworthy that the bot has, among other things, infrared
sensors, to which the developer has access.

The MPLAB IDE used to build the PIC programs can be downloaded for free from
http://www.microchip.com.

Specifics
"""""""""

The microcontroller model of the robot is a PIC 18F4550. It has two different
motors for each wheel. The motors can go either forward or backward. It also has
two obstacle sensors, which can be used to avoid the walls, and two infrared
sensors, which can be used to detect the line.

Obstacle sensors are set to 1 if an obstacle is detected, while infrared sensors
are set to 1 if the black line is detected.

Available pins are set up as follows::

    #define         motorLeftFwd    PORTC,1 ;Forward bit of left Motor
    #define         motorLeftBck    PORTC,0 ;Back bit of left Motor
    #define         motorRightFwd   PORTD,3 ;Forward bit of right Motor
    #define         motorRightBck   PORTC,2 ;Back bit of right Motor
    #define         obstacleLeft    PORTA,3 ;Right obstacle sensor 
    #define         obstacleRight   PORTA,2 ;Left obstacle sensor
    #define         infraredRight   PORTA,1 ;Right infrared sensor
    #define         infraredLeft    PORTA,0 ;Left infrared sensor

It is noteworthy that the bot's firmware relies on a a bootloader, which means
that PIC programs must start after a certain number of bytes. This can be seen
in the provided example.

Programs should be compiled using absolute addresses (no relocation).

Example
"""""""

The following program makes the robot run back and forth while trying to avoid
the walls::

    include         "p18F4550.inc"          ; including the header file of PIC 18F4550
    radix   hex             ; Unspecified literal hexadecimal-encoded


    ;********************************Label Definition***************************************
    #define         motorLeftFwd    PORTC,1 ;Forward bit of left Motor
    #define         motorLeftBck    PORTC,0 ;Back bit of left Motor
    #define         motorRightFwd   PORTD,3 ;Forward bit of right Motor
    #define         motorRightBck   PORTC,2 ;Back bit of right Motor
    #define         obstacleLeft            PORTA,3 ;Right obstacle sensor 
    #define         obstacleRight           PORTA,2 ;Left obstacle sensor

    temp1   equ     0x00    ;variable temp1 asociada a registro 0x000 de prop. General
    temp2   equ     0x01    ;variable temp2 asociada a registro 0x001 de prop. General
    temp3   equ     0x02    ;variable temp3 asociada a registro 0x002 de prop. general



            Org     0x200   ; Program begins at address 0x200
    ;********************************Configuration Section***************************************   
                    movlw   b'11111000'
                    movwf   TRISC                   ;RC0, RC1 y RC2 sets as OUTPUTS
                    movlw   b'11110111'
                    movwf   TRISD                   ;RD3 set as OUTPUT (Motor ports set as outputs)
                    setf    TRISA                   ;full PORTA set as INPUT (including sensors)
                    movlw   0x0f
                    movwf   ADCON1                  ;All ports digitals
                    movlw   0x07
                    movwf   CMCON                   ;Comparators Off

    ;********************************Program Starts***************************************
    goForward       bsf     motorRightFwd
                    bsf     motorLeftFwd
                    bcf     motorRightBck 
                    bcf     motorLeftBck
    detectRight     btfss   obstacleRight   ; if sensor is “1” skip next instruction (no detect)
                    bra     turnLeft                ; if previous instruction does not jump turn left
                                            ;       to avoid de obstacle detected

    detectLeft      btfss   obstacleLeft    ; if sensor is “1” skip next instruction (no detect)
                    bra     turnRight       ; if previous instruction does not jump turn Right
                                            ;       to avoid de obstacle detected
                    bra     goForward       ;

    turnLeft                Bsf     motorRightFwd
                    bcf     motorLeftFwd
                    bcf     motorRightBck 
                    bsf     motorLeftBck
                    rcall   halfSec         ;Wait 0,6s
                    bra     detectRight

    turnRight       Bcf     motorRightFwd
                    bsf     motorLeftFwd
                    bsf     motorRightBck 
                    bcf     motorLeftBck
                    rcall   halfSec                 ;Wait 0,6s
                    bra     detectLeft

    halfSec         Movlw   .3
                    movwf   temp1
                    clrf    temp2
                    clrf    temp3                   ; Init vars (temp0=8, temp1=0 y temp2=0)
    bucle1          decfsz  temp1, F                ; First loop is repeated 8 times.
                    bra     bucle2
                    return
    bucle2          decfsz  temp2, F                ; Second Loop is repeated 256 times for each 
                    bra     bucle3                          ;iteration of the first loop
                    bra     bucle1
    bucle3          decfsz  temp3, F                ; Third bucle is repeated 256 times for each 
                    bra     bucle3                          ;iteration of the second loop
                    bra     bucle2                          
    ;considering that each loop takes 3 cycles internal clock 
    ;(1 jump + 1 decrease), the loop takes 3 * 256 * 256 * 3 = 589825 
    ;as 1 cycle is 1 us, rutine takes aprox. 0.6 s

            End

Further details:
""""""""""""""""

Full documentation may be downloaded from:

* English: http://www.weblab.deusto.es/pub/docs/robot_module_english.docx
* Spanish: http://www.weblab.deusto.es/pub/docs/robot_module_spanish.docx

* **Target audience:** *engineering students in general, certain secondary schools*.

VISIR
-----

The `VISIR experiment <https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=Visir%20experiments&exp.name=visir>`_
lets you access the `BTH OpenLabs VISIR <http://openlabs.bth.se/electronics>`_
through WebLab-Deusto.

BTH OpenLabs VISIR (Virtual Instrument Systems In Reality) is a Remote
Laboratory developed in the `Blekinge Institute of Technology
<http://www.bth.se>`_, which supports remote experimentation with real
electronic circuits.

Students create circuits using the web interface, such as the following (where
two resistors, of 10k and 1k are placed in serial and connected to the Digital
MultiMeter):

.. image:: /_static/visir_circuit.png
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


* **Target audience:** It depends on how many principles are taught. It has been used with *secondary school students*, as well as with *electronics engineering courses*.
* **Video:** http://www.youtube.com/watch?v=vI5aM6Yq3S4

ud-logic
--------

`ud-logic <https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=PIC%20experiments&exp.name=ud-logic>`_
is a simple game implemented as an experiment. Players are presented with a
circuit diagram made up of 6 connected logic gates. Five of these gates show the
type of gate: AND, NAND, OR, NOR or XOR. The symbols, as described in `the
wikipedia <http://en.wikipedia.org/wiki/Logic_gate#Symbols>`_, are the
following:

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
**1**. Sometimes, several types might yield the desired result, and they will
all be considered correct.

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

* **Target audience:** *secondary school students*, as well as first course of certain engineerings.

Virtual Machine lab
-------------------

The `linux-vm
<https://www.weblab.deusto.es/weblab/client/#page=experiment&exp.category=VM%20experiments&exp.name=ud-linux-vm>`_
experiment gives you full access to a virtual machine running the Ubuntu Linux
distribution.

The user is presented with a few demo programs, among which is a sample Labview
application. The user is free to do whatever he wishes on the machine for the
assigned time, and the virtual machine will be reset by Weblab to its original
state once the session ends. For instance, you can test that the sudoku game
running in the virtual machine is always the same, since the state is always
restored.

The purpose of this experiment is mainly to showcase WebLab's ability to host
easy-to-develop unmanaged experiments.

More detailed and technical information on VM-based experiments is available
:ref:`here <deploying_vm_experiment>`.

.. image:: /_static/screenshots/weblab_vm.png
   :align: center

* **Target audience:** It depends on what equipment is used internally. The one running in the demo is only for demonstration purposes.
* **Video:** http://www.youtube.com/watch?v=b-L2LXRr23A
