
function wl_getIntProperty(name) 
{
	return parent.wl_getIntProperty(name);
}

function wl_getIntPropertyDef(name, defaultValue)
{
	return parent.wl_getIntPropertyDef(name, defaultValue);
}

function wl_getProperty(name)
{
	return parent.wl_getProperty(name);
}

function wl_getPropertyDef(name, defaultValue)
{
	return parent.wl_getPropertyDef(name, defaultValue);
}

function wl_sendCommand(command, commandId)
{
	return parent.wl_sendCommand(command, commandId);
}

function wl_onClean()
{
	return parent.wl_onClean();
}

function onHandleCommandResponse(a, b)
{
	alert(a);
}

function onHandleCommandError(a, b)
{
	alert(a);
}

var wl_inst = {}


parent.wl_inst.handleCommandResponse = function(msg, id)
{
	alert("On command response: " + msg);
}

parent.wl_inst.handleCommandError = function(msg, id)
{
	alert("On handleCommandError: " + msg);
}

parent.wl_inst.setTime = function(time)
{
	alert("On set time" + time);
}

parent.wl_inst.startInteraction = function()
{
	alert("OnStartInteraction");
	gfxinit();
}

parent.wl_inst.end = function()
{
	alert("OnEnd");
}

parent.wl_inst.handleFileResponse = function(msg, id)
{
	alert("On handle file response: " + msg);
}

parent.wl_inst.handleFileError = function(msg, id)
{
	alert("On handle file error: " + msg);
}



var Weblab = new function() {

    var internalFunction = function() {
    };

    this.sendCommand = function(text, successHandler, errorHandler) {
    };

	this.getProperty = function(name) {
		return wl_getProperty(name);
	};
	
	this.getPropertyDef = function(name, def) {
	    return wl_getPropertyDef(name, def);
	};

	this.getIntProperty = function(name) {
	    return wl_getIntProperty(name);
	};

	this.getIntPropertyDef = function(name, def) {
	    return wl_getIntPropertyDef(name, def);
	};
	
	this.clean = function () {
	    return wl_onClean();
	};
	
};
	