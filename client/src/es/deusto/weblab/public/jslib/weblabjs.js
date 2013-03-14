
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
	