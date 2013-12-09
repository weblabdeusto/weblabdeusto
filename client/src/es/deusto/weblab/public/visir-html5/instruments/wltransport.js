"use strict";
var visir = visir || {};

visir.WLTransport = function(workingCallback)
{
	this._isWorking = false;
	this._workCall = workingCallback;
	this._error = null;
	this.onerror = function(err){};
	this._session = null;

	this.Request("login", function(response)
	{
		response = $.parseJSON(response);

		if (visir.Config !== undefined)
		{
			visir.Config.Set("teacher", response.teacher);
		}

		visir._session = response.sessionkey;
	});
}

visir.WLTransport.prototype.Request = function(request, callback)
{
	trace("_SendRequest");

	if (request !== "login")
	{
		request = '<protocol version="1.3"><request sessionkey="'+visir._session+'">'+request+'</request></protocol>';
	}

	Weblab.sendCommand(request, callback, callback);
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