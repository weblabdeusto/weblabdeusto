Sample laboratories
===================

This section presents the a set of sample laboratories available in the
University of Deusto.

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

The FPGA laboratory, as other WebLab-Deusto laboratories (PIC or CPLD), is
developed within the WebLab-Box. On the WebLab-Box, the device, as well as a
`fit-pc <http://www.fit-pc.com/>`_, a PIC microcontroller, a camera, lighting
system and networking materials is installed, so as to make it easier to create
and deploy new laboratories.

.. image:: /_static/weblab_box.jpg
   :align: center

.. image:: /_static/WebLabBox.jpg
   :align: center


Aquarium
--------

**TO BE WRITTEN**

Robot
-----

robot-movement
^^^^^^^^^^^^^^

robot-proglist
^^^^^^^^^^^^^^

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
