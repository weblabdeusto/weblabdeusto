Romie = function(movements)
{
	this.topCamActivated = false;
	this.movements = movements;
}

Romie.prototype.forward = function(callback)
{
	if (this.movements != 0)
	{
		this.movements--;
		Weblab.sendCommand("F",
			function(response){
				if (this.hasTag(response))
				{
					console.log(this.getTag(response));
				}
				if (typeof callback == "function") callback();
				console.log(response);}.bind(this),
			function(response)
			{
				this.movements++;
				if (typeof callback == "function") callback();
				console.log(response);
			}.bind(this));
	}
}


Romie.prototype.left = function(callback)
{
	if (this.movements != 0)
	{
		this.movements--;
		Weblab.sendCommand("L",
			function(response)
			{
				if (typeof callback == "function") callback();
				console.log(response);
			},
			function(response)
			{
				this.movements++;
				if (typeof callback == "function") callback();
				console.log(response);
			}.bind(this));
	}
}

Romie.prototype.right = function(callback)
{
	if (this.movements != 0)
	{
		this.movements--;
		Weblab.sendCommand("R",
			function(response)
			{
				if (typeof callback == "function") callback();
				console.log(response);
			},
			function(response)
			{
				this.movements++;
				if (typeof callback == "function") callback();
				console.log(response);
			}.bind(this));
	}
}

Romie.prototype.checkWall = function(callback)
{
	Weblab.sendCommand("S",
		function(response)
		{
		//	if (response == "OK")
				if (typeof callback == "function") callback();
		//	else
		//		alert("TIENES UN MURO DELANTE");
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

Romie.prototype.getMovements = function()
{
	return this.movements;
}