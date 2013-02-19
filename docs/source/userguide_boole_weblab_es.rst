.. _toctree-directive:
.. _userguide_boole_weblab_es:

Boole-Deusto y Weblab-Deusto
============================

Introducción
------------

En esta guía se describe cómo utilizar Boole-Deusto con Weblab-Deusto. 
Las características de integración añadidas a Boole-Deusto hacen que sea posible y sencillo diseñar un
circuito combinacional o un autómata, y probarlo prácticamente al momento en un equipo real provisto
por Weblab-Deusto.

Boole-Deusto soporta dos tipos distintos de circuitos:

	* Circuitos combinacionales
	* Autómatas
	
Puesto que existen diferencias significativas entre ambos tipos, se dedicará a cada uno
una sección distinta de esta guías.


Circuitos Combinacionales
-------------------------


Introducción
^^^^^^^^^^^^

La mayor parte de características relacionadas con la creación de circuitos combinacionales 
no ha sufrido cambios con respecto al Boole-Deusto original.

El Boole-Deusto modificado tiene este aspecto:


.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional.png
	:width: 400 px
	:align: center


Como puede observarse, principalmente se han añadido algunos controles relacionados con Weblab
a la parte superior izquierda de la ventana.

En las secciones posteriores se describirá brevemente el propósito de estos nuevos controles, y
se incluirá una guía rápida paso a paso para crear y probar un sistema combinacional.


Controles de Weblab
^^^^^^^^^^^^^^^^^^^

Los controles añadidos a Boole-Deusto son dos, cuyo propósito se describirá brevemente a continuación.

Activación / desactivación de Weblab
....................................

.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional_weblabm.png
	:width: 300 px
	:align: center

Este control sirve para activar o desactivar el *modo weblab*. El *modo weblab*
puede ser activado o desactivado en cualquier momento. Cuando está desactivado, Boole-Deusto se comporta exactamente como
el Boole-Deusto original. Cuando está activado, sin embargo, se producen los siguientes efectos:
	  
	* Las tablas de entradas / salidas permiten elegir los nombres correctos, que se corresponden con las entradas / salidas en Weblab.
	* El código VHDL que Boole-Deusto genere será diferente al que normalmente generaría, ya que tendrá diversos cambios orientados
	  a hacerlo directamente compatible con el experimento FPGA de Weblab.
	  
.. Warning::
	El sistema permite, al igual que el Boole-Deusto original, pero incluso en modo weblab, asignar nombres arbitrarios de entradas y salidas, 
	o incluso repetir nombres existentes. Si bien el sistema en general funcionará de forma predecible al hacer ésto, los programas generados
	no serán compatibles (al menos, sin previa modificación) con Weblab-Deusto. Por eso, para facilitar el uso conjunto, se recomienda
	utilizar siempre nombres de la lista de entradas/salidas y nunca repetirlos.

.. Warning::
	En este momento existe un bug conocido que impide en ocasiones, estado en modo weblab, que aparezcan las sugerencias
	de entradas / salidas de Weblab. Debido a ciertos motivos, esto tiende a suceder siempre que se hace click por primera vez en 
	la primera celda de la tabla de entradas y de salidas. Para evitarlo, se recomienda hacer siempre click primero en otra celda.
	Es decir, en una celda que no sea la primera.
		  
Botón de apertura de Weblab
....................................

.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional_openweblabfpgam.png
	:width: 300 px
	:align: center

El botón "Open Weblab" abrirá una ventana del navegador que esté configurado por defecto, y generalmente tras dar
al usuario la posibilidad de autenticarse, accederá directamente al experimento FPGA, lo que permitirá al usuario subir inmediatamente el código
VHDL que genere y probarlo de forma rápida y sencilla.

.. Note:: 
	En este momento, el experimento Weblab-FPGA, que es el utilizado para probar el código VHDL, requiere un usuario registrado
	en Weblab que tenga ciertos privilegios. Sin dichos privilegios no será posible probar el código. En caso de que se necesiten 
	obtener tales privilegios, se recomienda ponerse en contacto con el equipo de Weblab-Deusto, o con quien corresponda.


Guía: Creando y probando un sistema combinacional
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

En el transcurso de esta breve guía, crearemos con Boole-Deusto un nuevo sistema combinacional,
que después probaremos directamente en WebLab utilizando las nuevas características de integración.

Para esta guía, se asume que el usuario está algo familiarizado con los sistemas combinacionales, y con
el Boole-Deusto original. 

	#. Comenzamos la creación de un sistema combinacional.
	#. Ahora, activaremos el modo Weblab, habilitando el control que se aprecia en la siguiente figura, y que nos
	   permitirá asignar fácilmente los nombres necesarios de las entradas/salidas, así como generar código VHDL
	   compatible con Weblab.

		.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional_weblabm.png
			:width: 300 px
			:align: center
	
	#. Con el modo Weblab habilitado, procedemos a dar un nomber al sistema, que en este caso será XOR-AND, ya que, como 
	   veremos enseguida, calcular el XOR y el AND será su tarea. 
	   
	#. Definimos dos entradas y dos salidas, y les asignamos en la tabla los nombres. En nuestro caso, las entradas se
	   corresponderán con los dos primeros "switches", mientras que las salidas se corresponderán con los dos primeros "leds". 
	   Es importante que los nombres utilizados sean exactamente los sugeridos por Boole-Deusto al estar en modo Weblab, ya
	   que es el nombre el que los relacionará posteriormente con los componentes físicos reales (switches, leds, etc) de los
	   que consta Weblab. Queda así:
	   
		.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional_io_asignadas.png
			:width: 400 px
			:align: center
			
	#. Hecho esto, definiremos normalmente la tabla de verdad para nuestro sistema. Es imprescindible hacer click en "evaluar" tras definirla.
	   La tabla que utilizaremos será la siguiente:
	
		.. image:: /_static/userguide_boole_weblab/tabla_verdad.png
			:width: 400 px
			:align: center
			
	#. Una vez definida la tabla de verdad, podemos, si así lo deseamos, hacer uso de las múltiples características que ofrece
	   Boole-Deusto, tales como visualizar el circuito o los diagramas que le corresponden. 
	   
	#. Para poder probar nuestro sistema combinacional en Weblab-Deusto, deberemos primero generar el código VHDL. Es **imprescindible**
	   asegurarse de que antes de generar el código, el modo Weblab esté habilitado. El código que se genera por defecto (en el modo
	   estándar) no es directamente compatible. Para generarlo, como en el Boole-Deusto tradicional, deberemos utilizar el botón que se
	   observa en la figura siguiente. Podemos nombrar al archivo VHDL como deseemos.
	   
		.. image:: /_static/userguide_boole_weblab/gen_vhdl.png
			:width: 300 px
			:align: center
			
	#. Con el código generado, ya estamos prácticamente listos para probar el sistema combinacional. Si lo deseamos, podemos echar
	   un vistazo al código que hemos generado, o incluso modificarlo, siempre que respetemos ciertas reglas impuestas por Weblab(principalmente, relacionadas
	   con los nombres de entradas y salidas). Para probarlo, haremos click en el botón "Open Weblab-FPGA", que abrirá un navegador:
	   
		.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional_openweblabfpgam.png
			:width: 300 px
			:align: center
			
	#. Una vez abierto el navegador en la página de Weblab, si no lo hemos hecho ya, deberemos autenticarnos. Una vez autenticados, llegaremos
	   a la pantalla del experimento Weblab-FPGA, en la cual deberemos elegir el archivo VHDL que hemos previamente generado, de tal forma:
	
		.. image:: /_static/userguide_boole_weblab/archivo.png
			:width: 300 px
			:align: center	
			
	#. Tras seleccionar el archivo, deberemos darle a "reserve", que reservará el experimento. Dependiendo del estado de Weblab-Deusto, y de la
	   la existencia o no de una cola de usuarios, transcurrirá más o menos tiempo antes de que la reserva concluya. La figura a continuación 
	   es la pantalla que veremos una vez realizada la reserva. 
	   
		.. image:: /_static/userguide_boole_weblab/compiling.png
			:width: 300 px
			:align: center	
	   
	#. Mientras esté presente la barra de progreso, el sistema estará, o bien sintetizando el código VHDL, o programando la placa. Puesto que
	   especialmente la sintetización es un proceso lento, pueden llegar a transcurrir varios minutos antes de que termine. Si la barra se detuviese
	   con un error, se recomienda consultar la advertencia que se incluye al final de esta sección. El resto de la guía asume que tanto la sintetización
	   como la programación son correctas.
	   
	#. Una vez que el programa ha sido correctamente sintetizado, y la placa correctamente grabada, veremos algo similar a lo siguiente:
	
		.. image:: /_static/userguide_boole_weblab/fulludfpga.png
			:width: 500 px
			:align: center
			
	#. Finalmente, vemos que disponemos en primer lugar de una webcam, por la que podemos ver la placa física, que está actualmente ejecutando nuestro sistema
	   combinacional. Podemos ver también los leds, que actúan como salidas, y diversos interruptores virtuales, que actúan como entrada física real a
	   la placa, y mediante los cuales podemos interactuar. En este caso, vemos que con los interruptores a "0-1" está encendido el segundo LED, y apagado el primero, tal y como
	   hemos definido en nuestra tabla de verdad.
	   
	#. Disponemos de un tiempo limitado para probar el sistema. Una vez que el tiempo expire, el sistema automáticamente volverá a la pantalla de reserva. Si necesitamos realizar
	   más pruebas, deberemos reservar de nuevo. 
			
.. Note:: 
	Los leds (*Leds<0-8>*), los interruptores (*Switches<0-9>*) y los botones (*Buttons<0-3>*) se ordenan de derecha a izquierda. Esto implica, por ejemplo, que el
	*Switch<0>* en Boole-Deusto se corresponde con el interruptor de más a la derecha, mientras que el *Switch<1>* sería el inmediatamente a su izquierda.
	
.. Warning::
	Si la barra se detuviese con un "compiling error" o con un "programming error", significaría, en el primer caso, que el proceso de sintetización 
	ha fallado (quizás debido a un error de sintáxis), y en el segundo, que el proceso de programación de la placa ha fallado.
	Si el error es del primer tipo (compiling error) se recomienda:
	
		* Comprobar que se ha seleccionado el VHDL correcto.
		* Comprobar que el VHDL se ha generado en modo Weblab.
		* Comprobar que todas las entradas y salidas utilizan nombres válidos de la lista de entradas y salidas de Weblab, y que 
		  por tanto no se han incluido entradas/salidas con nombres originales, ni entradas/salidas con nombres repetidos.
		* Comprobar que no se hayan realizado modificaciones manuales al VHDL, o que en caso de que se hayan realizado, no contengan
		  errores.
		  
	Si con las diversas comprobaciones anteriores no se consigue resolver el problema, o si el error es de programación (grabación), se recomienda:
		* Esperar un tiempo, y volver a intentarlo más tarde.
		* Contactar con los administradores de Weblab-Deusto.



Autómatas
-------------------------


Introducción
^^^^^^^^^^^^

El segundo tipo de circuito con el que Boole-Deusto puede trabajar son los autómatas. Esta característica, que ya existía en el boole-deusto original, ha sido extendida añadiendo capacidad de integración inmediata con Weblab-Deusto y en concreto sus experimentos FPGA. Tras esta extensión, es ahora posible diseñar y definir un autómata gráficamente, e inmediatamente observarlo en funcionamiento (e interactuar con él) en un FPGA físico real en Weblab-Deusto.


Aspectos básicos con Weblab-Deusto
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Nombres de las entradas y salidas
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

En su versión actual, para promover la simplicidad, esta parte de Boole-Deusto no requiere (ni permite) elegir las correspondencias entre las salidas y entradas de los estados, y las salidas
y entradas de Weblab-Deusto. En vez de eso, se ha de saber que la correspondencia entre entradas y salidas siempre es la misma:

Las entradas son siempre los interruptores. De este modo, si tenemos por ejemplo un estado S0 que "recibe" dos entradas,
estas dos entradas se corresponderán con los últimos dos interruptores (los de más a la derecha). 

Las salidas son siempre los LEDs. De este modo, si tenemos un estado S0 que tiene dos salidas, estas dos salidas se corresponderán con los últimos dos LEDs (los de más a la derecha).
Si la salida del estado es por ejemplo "01", el LED de más a la derecha estará encendido, y el LED inmediatamente a su izquierda apagado.

Botón de reset
,,,,,,,,,,,,,,

Existe un botón que devuelve al autómata a su estado inicial. Este botón es siempre el último botón de Weblab (el de más a la derecha). 


Controles de Weblab
^^^^^^^^^^^^^^^^^^^

Los controles añadidos a Boole-Deusto en la integración con Weblab-Deusto son principalmente de dos tipos:

Exportación a código Weblab-VHDL
................................

.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional_weblabm.png
	:width: 300 px
	:align: center
	
Mediante el uso de estas opciones, es posible generar código VHDL que sea inmediatamente compatible con el experimento FPGA de Weblab-Deusto.
Para conseguir esta compatibilidad, el código generado utilizará nombres de entradas y salidas compatibles con las de Weblab-Deusto (definidas en un UCF).

Podemos observar que existen varias opciones para generar el código. Cada una de esas opciones corresponde a un tipo de reloj diferente, que utilizará el
autómata. Los relojes disponibles son los siguientes:

Reloj Interno (Internal Clock)
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Utiliza el reloj interno de la FPGA. Su frecuencia es bastante alta, lo que lo hace poco adecuado para aquellos casos en los que el comportamiento del autómata 
requiera de alguna clase de sincronización de las entradas y salidas con el reloj.

Reloj Weblab (Weblab Clock)
,,,,,,,,,,,,,,,,,,,,,,,,,,,

Algo más lento que el reloj interno. Está provisto por el propio Weblab-FPGA, y su frecuencia puede ser controlada de forma limitada, mediante un *slider* en el propio experimento.

Reloj Interruptor (Switch Clock)
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

El último interruptor (el de más a la izquierda) actúa como reloj. Esto lo hace muy adecuado para aquellos casos en los que se desee probar el autómata teniendo un absoluto control sobre el reloj. Esto podría incluir, por ejemplo, aquellos casos en los que es necesario sincronizar las entradas con él.

Reloj Botón (Button Clock)
,,,,,,,,,,,,,,,,,,,,,,,,,,

Similar al anterior, en este caso el botón de más a la izquierda actúa como reloj. De nuevo, muy adecuado para aquellos casos en los que se desee probar el autómata teniendo un absoluto control sobre el reloj.

.. Warning::
	Debido a limitaciones presentes ya en el Boole-Deusto original, se recomienda comprobar el autómata antes de intentar generar el código. Ciertos errores, como el no asignar salidas a un estado, pueden
	hacer que el programa deje de responder.

.. Warning::
	Si se utiliza la generación de código VHDL estándar de Boole-Deusto (la que no hace mención sobre relojes, ni sobre Weblab), el VHDL generado NO será compatible con Weblab-Deusto. Al menos, sin aplicar manualmente grandes modificaciones.
	  
.. Note::
	**Nota de implementación**
	En la práctica, el reloj a utilizar no lo determina el VHDL en sí, sino el archivo de restriccines (UCF) que se utilice. Boole-Deusto añade una directiva como comentario al VHDL, como por ejemplo ```%%%CLOCK:SWITCH%%%```.
	Esta directiva, en absoluto original de Xilinx, es detectada por el propio Weblab-Deusto, que sintetizará el VHDL provisto utilizando un UCF u otro. Cuando se utiliza Weblab-Deusto FPGA también es posible usar dichas directivas en código VHDL escrito manualmente.

		  
Apertura de Weblab
....................................

.. image:: /_static/userguide_boole_weblab/nuevo_sist_combinacional_openweblabfpgam.png
	:width: 300 px
	:align: center

El botón "Open Weblab" abrirá una ventana del navegador que esté configurado por defecto, y generalmente tras dar
al usuario la posibilidad de autenticarse, accederá directamente al experimento FPGA, lo que permitirá al usuario subir inmediatamente el código
VHDL que genere y probarlo de forma rápida y sencilla.

.. Note:: 
	En este momento, el experimento Weblab-FPGA, que es el utilizado para probar el código VHDL, requiere un usuario registrado
	en Weblab que tenga ciertos privilegios. Sin dichos privilegios no será posible probar el código. En caso de que se necesiten 
	obtener tales privilegios, se recomienda ponerse en contacto con el equipo de Weblab-Deusto, o con quien corresponda.

.. Note::
	Esta sección del manual, y el propio Boole-Deusto en lo relacionado a estos aspectos, se encuentran actualmente en desarrollo. 

