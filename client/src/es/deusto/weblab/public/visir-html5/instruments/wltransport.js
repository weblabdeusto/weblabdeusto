"use strict";

var visir = visir || {};
visir.WLTransport = function(workingCallback)
{
	this._isWorking = false;
	this._workCall = workingCallback;
}

visir.JSTransport.prototype.Request = function(request, callback)
{
	trace("Send request");

	if (!navigator.onLine) {
		alert("Check your internet connection and try again.");
		return;
	}

	this._error = null;
	if (this._isWorking) return;
	this.SetWorking(true);
	if (!this._IsAuthenticated()) {
		this._SendAuthentication(request, this._cookie, callback);
	}
	else
	{
		this._SendRequest(request, callback);
	}
}