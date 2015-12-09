# Guía de FPGA-Watertank

## Introducción

FPGA-Watertank te permite utilizar un Laboratorio Remoto Aumentado.
Un Laboratorio Remoto Aumentado, como en este caso, es un Laboratorio que
tiene además de los componentes reales uno o varios componente virtuales.

En este caso, el componente virtual es un tanque de agua. Mediante la placa
 FPGA real es posible controlar el modelo virtual.


## El modelo virtual

El tanque de agua es un sistema formado por el depósito de agua,
dos bombas, tres sensores de nivel, dos sensores de sobrecalentamiento, y una
demanda de agua variable.

Como diseñador de la lógica, mediante la placa FPGA tendrás la posibilidad
de controlar las bombas (los actuadores) así como de leer las entradas (los
cinco sensores).


### Mapeo de sensores y actuadores

Los actuadores (bombas de agua) se controlan mediante las salidas led de la
placa FPGA. Los sensores se leen mediante las entradas *interruptor*. En concreto,
el mapeo es éste:

Sensor      | Indica en el modelo              | Salida en FPGA
----------- | -------------------------------- | --------------
Nivel bajo  | 20% de altura del depósito       | swi_0
Nivel medio | 50% de altura del depósito       | swi_1
Nivel alto  | 80% de altura del depósito       | swi_2
Sobrecal.   | Sobrecalentamiento bomba izq.    | swi_3
Sobrecal.   | Sobrecalentamiento bomba dcha.   | swi_4


Actuador    | Acción                     | Entrada en FPGA
----------- | -------------------------- | ---------------
Bomba Izq.  | Activa la bomba izquierda  | led_0
Bomba Dcha. | Activa la bomba derecha    | led_1


### Funcionamiento del modelo

El modelo es un tanque de agua. El agua que sale del depósito (que representa)
la demanda varía aleatoriamente en el tiempo, y el usuario (a través de la placa
FPGA) no tiene control sobre ella.

El usuario tiene la capacidad de activar o desactivar cada una de las dos bombas
de agua. Cuando la salida *led_0* se activa, la bomba izquierda se activa.
Cuando la salida *led_1* se activa, la bomba derecha se activa. Cuando una bomba
está activada, introducirá agua en el depósito, lo que tenderá a aumentar el
**nivel
de agua**. A la vez, mientras una bomba está encendida, aumenta su **temperatura**.
Mientras una bomba está apagada, su **temperatura** desciende (hasta llegar a 20ºC).

Cuando el nivel de agua va llegando al nivel de los sensores (20%, 50%, 80%)
éstos se van activando. Los sensores están representados en el modelo como
bombillas rojas.

Existen además dos sensores de sobrecalentamiento, que no son visibles en el modelo
virtual, y que estarán activados para cada bomba siempre que la temperatura sea mayor
de **200ºC**.


## Generación de VHDL

El código VHDL a enviar puede ser creado a mano, o generado utilizando
Boole-Deusto.

Generando con Boole-Deusto se soportan tanto **sistemas combinacionales** como
**sistemas secuenciales**. Se deben tener muy en cuenta las siguientes
recomendaciones.

Para sistemas combinacionales:
 * Asegurarse de que se ha activado el *modo weblab* antes de generar el código
 * Asegurarse de que se han asignado nombres específicos a las entradas y salidas.
   Los posibles nombres son fijos. Deberán aparecer en una lista al asignarlos en modo
   WebLab.

Para sistemas secuenciales:
 * Asegurarse de que al generar el código se utiliza el **reloj weblab**.
 * En general tendrán 1 o 2 salidas (que automáticamente se dirigirán a los leds).
 * En general tendrán de 1 a 5 entradas (que serán los sensores; en orden: swi0, swi1, swi2, swi3, swi4).
 * *No* será necesario especificar explícitamente en este caso los nombres "físicos" de las entradas y salidas.


## Utilización del sistema

Para utilizarlo, es necesario acceder a la página y se recomienda esperar a que
la visualización  se cargue completamente. Hecho ésto, y preparado el programa,
debe **reservarse** el experimento. Una vez reservado, se deberá **seleccionar**
el archivo VHDL y **subir** el archivo. Comenzará el proceso de sintetización.
Sintetizar el VHDL es un proceso lento y a veces llevará
**varios minutos**. Cuando termine, se programará la placa FPGA, el modelo
virtual se reiniciara automáticamente, y la lógica comenzará a ejecutarse.



