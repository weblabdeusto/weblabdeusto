/*
* Copyright (C) 2005-2009 University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Luis Rodriguez Gil <luis.rodriguez@opendeusto.es>
*
*/ 


package weblab.util{
	import flash.external.ExternalInterface;
	import flash.utils.Dictionary;
	import flash.utils.Timer;
	import flash.events.TimerEvent;

	//! Singleton class to help develop experiment interfaces in Flash. 
	//! Provides several javascript callbacks (which can be set by calling the registerCallbacks
	//! method) and it permits the sending of commands and the retrieval of their responses
	//! asynchroneously through custom on success and on error delegates provided when sending it.
	public class WeblabFlash {
		
		public static const STATE_WAITING : int = 0;
		public static const STATE_INTERACTING : int = 1;
		public static const STATE_FINISHED : int = 2;
		
		private var mTimer : Timer = new Timer(1000);
		
		private var mCurrentState:int = STATE_WAITING;
		private var mTimeLeft:int = 0;
		
		private var mLastId:int=0;
		private var mCommandDict : Dictionary = new Dictionary();
		private var mEndCallback, mStartInteractionCallback, mSetTimeCallback : Function;
		private var mOnSecondEllapsedCallback;

		private static var mInstance : WeblabFlash = new WeblabFlash();


		//! Generates and returns a new unique command id.
		//!
		private function getNewCommandId():int {
			return mLastId++;
		}

		//! Stores the callbacks of a new command and generates an ID to identify them and the command.
		//! 
		//! @param onSuccess Function to call if the command succeeds.
		//! @param onError Function to call if the command fails.
		//! @return An unique id for the command, which will link it to its callbacks.
		private function addCommandCallbacks(onSuccess : Function, onError : Function):int {
			var id:int=getNewCommandId();
			var callback_array:Array=new Array(onSuccess,onError);
			mCommandDict[id]=callback_array;
			return id;
		}

		//! Returns the current state of the flash app as an integer.
		//!
		//! @return STATE_WAITING if we have not been told to start interaction.
		//! 		STATE_INTERACTING if we are interacting.
		//!			STATE_FINISHED if we received onEnd().
		public function getCurrentState() : int
		{
			return mCurrentState;
		}
		
		//! Returns the number of seconds left of experiment.
		//!
		public function getTimeLeft() : int
		{
			return mTimeLeft;
		}

		
		//! Calls the Javascript function debugMsg passing it msg.
		//!
		public function debugMsg(msg : String)
		{
			trace(msg);
			//ExternalInterface.call("debugMsg", msg);
		}
		
		//! This function returns the string that it gets passed. Its main purpose
		//! is to test whether the JS/Flash connection is working as expected.
		//! 
		//! @param msg The string that will be returned.
		//! @return The string passed to the func.
		private function handleTestEcho(msg : String)
		{
			return msg;
		}

		//! ----- Constructor ------
		//! Note: This ctor should actually be private but apparently private ctors are 
		//! not currently supported by AS3.
		public function WeblabFlash() {
			
			if( mInstance != null )
				throw new Error("WeblabFlash must not be instanced. Instead, getInstance() must be called to access the only instance.");
				
			
			ExternalInterface.addCallback("testEcho", handleTestEcho);
			
			ExternalInterface.addCallback("handleCommandResponse", handleCommandResponse);
			ExternalInterface.addCallback("handleCommandError", handleCommandError);
			
			ExternalInterface.addCallback("setTime", onSetTime);
			ExternalInterface.addCallback("startInteraction", onStartInteraction);
			ExternalInterface.addCallback("end", onEnd);
			
			mTimer.addEventListener("timer", onSecondEllapsed);
			mTimer.start();
		}
		
		private function onSecondEllapsed(args : TimerEvent) : void
		{
			if( (mTimeLeft > 0) && (mCurrentState != STATE_WAITING) )
				mTimeLeft--;
			if( mTimeLeft == 0 && mCurrentState == STATE_INTERACTING )
			{
				mCurrentState = STATE_FINISHED;
				onClean();
			}
			if(mOnSecondEllapsedCallback != null)
				mOnSecondEllapsedCallback();
		}
		
		// ------- Internal Javascript callbacks. They will forward to the user-defined callback
		// if it is present. They do nothing otherwise. ------
		
		private function onSetTime(time : int) {
			mTimeLeft = time;
			if( mSetTimeCallback != null )
				mSetTimeCallback(time);
		}
		
		private function onStartInteraction() : void {
			mCurrentState = STATE_INTERACTING;
			if( mStartInteractionCallback != null )
				mStartInteractionCallback();
		}
		
		private function onEnd() : void {
			mCurrentState = STATE_FINISHED;
			if( mEndCallback != null )
				mEndCallback();
		}
		
		// ------- Command response javascript callbacks. The commandId identifies
		// the command they belong -------
		
		function handleCommandResponse(msg : String, commandId : int):void {
			mCommandDict[commandId][0](msg);
			delete mCommandDict[commandId];
		}

		function handleCommandError(msg : String , commandId : int):void {
			mCommandDict[commandId][1](msg);
			delete mCommandDict[commandId];
		}

		//! Retrieves a reference to the only instance of WeblabFlash.
		//!
		public static function getInstance() : WeblabFlash {
			return mInstance;
		}

		
		//! Registers the JS callbacks setTime, startInteraction and end, so that
		//! the appropiate user-specified delegate is automatically called when appropiate.
		//! Optionally registers a seconds timer.
		//!
		//! @param setTime Function called to set the time.
		//! @param startInteraction Function called to start interacting with the user.
		//! @param end Function called when the experiment ends.
		//! @param onSecondEllapsed Function called every second.
		public function registerCallbacks(setTime : Function, startInteraction : Function, end : Function, onSecondEllapsed : Function = null) : void
		{
			mSetTimeCallback = setTime;
			mStartInteractionCallback = startInteraction;
			mEndCallback = end;
			mOnSecondEllapsedCallback = onSecondEllapsed;
		}

		// ------- Provides a simple interface to obtain properties from 
		// Note: AS3 doesn't support function overloading so we use the null
		// default parameter workaround.

		//! Retrieves a property as a string.
		//!
		//! @param prop The name of the property.
		//! @param def The default value to return if the property is not found.
		public function getPropertyDef( prop : String, def : String):String {
			return ExternalInterface.call("wl_getPropertyDef", prop, def);
		}
		
		//! Retrieves a property as a string.
		//!
		//! @param prop The name of the property.
		public function getProperty( prop : String ):String {
			return ExternalInterface.call("wl_getProperty", prop);
		}

		//! Retrieves an integer property.
		//!
		//! @param prop The name of the property.
		//! @param def The default value to return if the property is not found.
		public function getIntPropertyDef( prop : String, def : int ):int {
			return ExternalInterface.call("wl_getIntPropertyDef", prop, def);
		}
		
		//! Retrieves an integer property.
		//!
		//! @param prop The name of the property.
		public function getIntProperty( prop : String ):int {
			return ExternalInterface.call("wl_getIntProperty", prop);
		}
		
		//! Indicates that the experiment is finished.
		//!
		public function onClean():void {
			mCurrentState = STATE_FINISHED;
			ExternalInterface.call("wl_onClean");
		}

		//! Sends a command to the server. Its response will be received asynchroneously through
		//! two alternative callbacks.
		//! 
		//! @param command_str The command string.
		//! @param onSuccess Function to call if the command succeeds. Should take the response string
		//! as a parameter.
		//! @param onError Function to call if the command fails. Should take the response string
		//! as a paramter.
		public function sendCommand(command_str : String, onSuccess : Function, onError : Function) {
			var id : int = addCommandCallbacks(onSuccess,onError);
			
			debugMsg("DBG: " + command_str);
			ExternalInterface.call("wl_sendCommand", command_str, id);
		}

	}

}