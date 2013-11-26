"use strict";

var visir = visir || {};
visir.WLTransport = function(workingCallback)
{
	this._isWorking = false;
	this._workCall = workingCallback;
	this._error = null;
	this.onerror = function(err) {};
}

visir.WLTransport.prototype.Request = function(request, callback)
{
	trace("_SendRequest");

	Weblab.sendCommand(request, function(resp){trace("CORRECTO: "+resp);}, function(resp){trace("ERROR: "+resp);});
}

/*
	func is a callback function that the transport system can call to make a new request
*/
visir.WLTransport.prototype.SetMeasureFunc = function(func)
{
	trace("SetMeasureFunc");
}

visir.WLTransport.prototype.SetWorking = function(isWorking, shouldContinue)
{
	shouldContinue = (shouldContinue == undefined) ? true : shouldContinue;
	this._isWorking = isWorking;
	if (typeof this._workCall == "function") this._workCall(isWorking, shouldContinue);
	$("body").trigger({ type:"working", isWorking: isWorking, shouldContinue: shouldContinue });
}

visir.WLTransport.prototype.Error = function(errormsg) {
	this.SetWorking(false, false);
	trace(errormsg);
	this.onerror(errormsg);
	this._error = errormsg;
}