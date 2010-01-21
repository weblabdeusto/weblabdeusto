
************
INTRODUCTION
************

The class WeblabFlash aims to make the creation of new experiments in flash easier,
handling Javascript-Flash interaction and the internal experiment timer.


**************
INITIALIZATION
**************

In order to create a new experiment using WeblabFlash, weblab.util.WeblabFlash must be imported.

Done this, it is possible to access the singleton instance of WeblabFlash through its static method
getInstance().

After getting a reference to this instance the programmer should register the weblab callbacks.
This is done through the registerCallbacks method. The callback functions to call whenever events
take place are passed to registerCallbacks as parameters. If being notified of a certain event is not
required, it is possible to pass null for it instead. Events are, in order: onSetTime, 
onStartInteraction, onEnd, onSecondEllapsed. This last one is null by default and hence may 
not be passed at all.


****************
SENDING COMMANDS
****************

The method sendCommand is used to send commands to the server. It takes a string with the command as first
parameter plus two callback functions. First of those will be called in case the command succeeds and
the other one in case it fails. Both callbacks are passed a message string when called.


******
STATES
******

A WeblabFlash experiment may be found in one of three different states.

WeblabFlash.STATE_WAITING: When weblab is yet to call startInteraction.

WeblabFlash.STATE_INTERACTING: When startInteraction has been called and therefore the experiment has 
started, and is not done yet.

WeblabFlash.STATE_FINISHED: When weblab has called onEnd() or when onClean() has been called locally.


Current state may be obtained through the getcurrentState() method.


***********************
TIMING AND FINALIZATION
***********************

The time of an experiment is limited. WeblabFlash internally keeps a timer. This timer is 
initialized to the value passed by weblab through its setTime() call and starts decreasing once
interaction starts. When zero is reached, onClean() is automatically called and the experiment 
is considered to be finished. onClean() may also be called explicitally before the timer reaches zero.
Moreover, weblab may call onEnd() at any time to finish the experiment. Whenever this happens, the
programmer is responsible to clean all resources in use (such as timers).
