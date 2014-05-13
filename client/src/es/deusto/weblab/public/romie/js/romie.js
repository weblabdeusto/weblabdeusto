Romie = function(movements)
{
	this.topCamActivated = false;
	this.movements = movements;
	this.points = 0;
	this.moving = false;
	this.lastResponse = null;
	this.topTime = 10;
	this.updater = null;
}

Romie.prototype.forward = function(callback)
{
	if (this.movements != 0)
	{
		this.movements--;
		this.moving = true;
		Weblab.sendCommand("F",
			function(response){
				this.lastResponse = response;
				if (this.hasTag())
				{
					console.log(this.getTag());
				}
				this.moving = false;
				if (typeof callback == "function") callback();
				console.log(response);
			}.bind(this), function(response)
			{
				this.lastResponse = response;
				this.movements++;
				this.moving = false;
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
		this.moving = true;
		Weblab.sendCommand("L",
			function(response)
			{
				this.lastResponse = response;
				this.moving = false;
				if (typeof callback == "function") callback();
				console.log(response);
			}.bind(this),
			function(response)
			{
				this.lastResponse = response;
				this.movements++;
				this.moving = false;
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
		this.moving = true;
		Weblab.sendCommand("R",
			function(response)
			{
				this.lastResponse = response;
				this.moving = false;
				if (typeof callback == "function") callback();
				console.log(response);
			}.bind(this),
			function(response)
			{
				this.lastResponse = response;
				this.movements++;
				this.moving = false;
				if (typeof callback == "function") callback();
				console.log(response);
			}.bind(this));
	}
}

Romie.prototype.hasTag = function()
{
	return this.lastResponse !== null && this.lastResponse.indexOf("Tag:") != -1;
}

Romie.prototype.getTag = function()
{
	return this.lastResponse.substring(5, this.lastResponse.length-6);
}

Romie.prototype.activateTopCam = function()
{
	this.topCamActivated = true;

	this.updater = setInterval(function()
	{
		if (this.topCamActivated)
			this.topTime--;
		else
			this.deactivateTopCam();
	}, 1000);
}

Romie.prototype.deactivateTopCam = function()
{
	this.topCamActivated = false;
	clearInterval(this.updater);
}

Romie.prototype.isTopCamActivated = function()
{
	return this.topCamActivated;
}

Romie.prototype.getMovements = function()
{
	return this.movements;
}

Romie.prototype.addMovements = function(moves)
{
	this.movements += moves;
}

Romie.prototype.setMovements = function(moves)
{
	this.movements = moves;
}

Romie.prototype.addPoints = function(points)
{
	this.points += points;
}

Romie.prototype.setPoints = function(points)
{
	this.points = points;
}

Romie.prototype.substractPoints = function(points)
{
	this.points -= points;
	if (this.points < 0) this.points = 0;
}

Romie.prototype.getPoints = function()
{
	return this.points;
}

Romie.prototype.isMoving = function()
{
	return this.moving;
}