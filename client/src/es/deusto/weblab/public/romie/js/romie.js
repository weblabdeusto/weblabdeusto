Romie = function()
{
	this.topCamActivated = false;
}

Romie.prototype.forward = function()
{
	Weblab.sendCommand("F",
		function(response){
			if (this.hasTag(response))
			{
				console.log(this.getTag(response));
			}
			console.log(response);},
		function(response){console.log(response);});
}


Romie.prototype.left = function()
{
	Weblab.sendCommand("L",
		function(response){console.log(response);},
		function(response){console.log(response);});
}

Romie.prototype.right = function()
{
	Weblab.sendCommand("R",
		function(response){console.log(response);},
		function(response){console.log(response);});
}

Romie.prototype.checkWall = function(callback)
{
	Weblab.sendCommand("S",
		function(response)
		{
			if (response == "OK")
				callback();
			else
				alert("TIENES UN MURO DELANTE");
		},
		function(response){console.log(response);});
}

Romie.prototype.hasTag = function(response)
{
	return response.indexOf("Tag:") != -1;
}

Romie.prototype.getTag = function(response)
{
	return response.substring(5, response.length-4);
}

Romie.prototype.activateTopCam = function()
{
	this.topCamActivated = true;
}

Romie.prototype.deactivateTopCam = function()
{
	this.topCamActivated = false;
}

Romie.prototype.isTopCamActivated = function()
{
	return this.topCamActivated;
}