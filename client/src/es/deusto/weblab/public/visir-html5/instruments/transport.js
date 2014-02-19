"use strict";

var visir = visir || {};
visir.JSTransport = function(workingCallback)
{
	this._url = "";
	this._cookie = "nocookieforyou";
	this._isWorking = false;
	this._workCall = workingCallback;
	this._sessionKey = null;
	this._error = null;
	this.onerror = function(err) {};

	this._request = this._CreateRequest();

	this._shuttingDown = false;

	var me = this;
	$(window).bind('beforeunload', function() {
	//$(window).unload(function() {
		trace("shutting down");
		me._shuttingDown = true;
	});
}

/*
	If not authenticated, this will first try to get a session key from the server
	If that succeeds, it will send the request to the server, get a response and pass that back through the callback
	On error, call onerror

	request: instrument xml to transport
	callback: a function that takes a xml blob with reponse data
*/
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

/*
	func is a callback function that the transport system can call to make a new request
*/
visir.JSTransport.prototype.SetMeasureFunc = function(func)
{
	trace("SetMeasureFunc");
}

visir.JSTransport.prototype.Connect = function(url, cookie)
{
	trace("connecting: " + url + " " + cookie);
	this._url = url;
	this._cookie = cookie;
}

visir.JSTransport.prototype.SetWorking = function(isWorking, shouldContinue)
{
	shouldContinue = (shouldContinue == undefined) ? true : shouldContinue;
	this._isWorking = isWorking;
	if (typeof this._workCall == "function") this._workCall(isWorking, shouldContinue);
	$("body").trigger( { type:"working", isWorking: isWorking, shouldContinue: shouldContinue });
}

/*
	Add the protocol and request tags to the request and send it to the server
*/
visir.JSTransport.prototype._SendRequest = function(xmlstring, callback)
{
	trace("_SendRequest");
	var xmlstring = '<root><protocol version="1.3"><request>' + xmlstring + '</request></protocol></root>';
	var $req = $(xmlstring);
	if (this._sessionKey) $req.find("protocol > request").attr("sessionkey", this._sessionKey);

	var data = $req.html();
	//trace(data);
	var tprt = this;
	this._SendXML(data, function(response) {
		//trace("reponse: " + response);
		tprt.SetWorking(false);
		if (typeof callback == "function") {
			// this will check for errors in the request
			var ret = tprt._ReadResponseProtocolHeader(response);
			// and we only want to do the callback if there is no errors
			if (!tprt._error) {
				callback(ret);
			}
		}
	});
}

visir.JSTransport.prototype._AuthReadSessionKey = function(response)
{
	trace("_AuthReadSessionKey");
	var $xml = $(response);
	var sessionKey = $xml.find("login").attr("sessionkey");
	trace("AuthCallback session key: " + sessionKey);
	if (sessionKey) this._sessionKey = sessionKey;
}

visir.JSTransport.prototype._ReadResponseProtocolHeader = function(response)
{
	var $xml = $(response);
	if ($xml.find("response").length > 0) {
		return $xml.html(); // this will strip of the outer protocol tags
	}
	var $error = $xml.find("error");
	if ($error.length > 0)
	{
		this.Error($error.text());
		return;
	}
	this.Error("Unable to parse response");
}


visir.JSTransport.prototype._SendAuthentication = function(request, cookie, callback)
{
	trace("_SendAuthentication");
	var xml = '<protocol version="1.3"><login keepalive="1" cookie="' + cookie + '"/></protocol>';
	var tprt = this;
	this._SendXML(xml, function(response) {
		tprt._AuthReadSessionKey(response);
		// make sure everything went well..
		tprt._SendRequest(request, callback);
	});
}

visir.JSTransport.prototype._CreateRequest = function()
{
	//return new XMLHttpRequest();

	if (window.XDomainRequest) {
		// ie.. untested..
		var req = new window.XDomainRequest();
	} else {
		var req = new XMLHttpRequest();
	}

	return req;
}

/*
* XXX: I can't find a way to make sure that requests are pipelined in the same connection to the webserver
*/
visir.JSTransport.prototype._SendXML = function(data, callback)
{
	var me = this;
	// for some reason the jquery post doesn't work as it should, try again in the future.
	if (window.XDomainRequest) {
		// ie.. untested
		var req = this._request; //new window.XDomainRequest();
		req.onload = function() {
			trace("xdomain: " + req.responseText);
			callback(req.responseText);
			req = me._CreateRequest();
	 	};

		req.onerror = function(e) {
			trace("xdomain error: " + e);
		};
		req.open('POST', this._url, true);
		//req.send(data);
		setTimeout( function() { req.send(data);}, 100);

	} else {
		var req = this._request; //new XMLHttpRequest();
		req.open('POST', this._url, true);
		req.timeout = 5000;
		req.onerror = function(e) {
			trace("XMLHttpRequest error: " + e);
			var errtext = "XMLHttpRequest error, webservice is not responding to requests.";
			me.Error(errtext);
		}
		req.ontimeout = function() { trace("XMLHttpRequest timeout"); me.Error("Webservice not responding. Contact the system administrator."); }
		req.onreadystatechange = function(response)
		{
			if (me._shuttingDown) return;
			if (req.readyState != 4) return;
			if (req.status == 0) return; // workaround for strange shutdown status
			if (req.status != "200" && req.status != "304") {
				me.Error("unexpected request return status: " + req.status + " " + req.readyState);
				return;
			}
			//trace("XMLHttpRequest response: " + req.responseText);
			callback(req.responseText);
		};
		req.send(data);
	}
}

visir.JSTransport.prototype._IsAuthenticated = function()
{
	return (this._sessionKey != null);
}

visir.JSTransport.prototype.Error = function(errormsg) {
	this.SetWorking(false, false);
	trace(errormsg);
	this.onerror(errormsg);
	this._error = errormsg;
	this._sessionKey = null; // XXX: all errors lead to requthentication
}