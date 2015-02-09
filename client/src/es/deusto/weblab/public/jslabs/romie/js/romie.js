Romie = function()
{
	this.moving = false;
	this.lastResponse = null;
}

Romie.prototype.forward = function(callback)
{
	if ( ! this.moving)
	{
		this.moving = true;
		Weblab.sendCommand("F",
			function(response){
				this.lastResponse = response;
				if (this.hasTag())
				{
					console.log(this.getTag());
					callback(this.getTag());
				}
				this.moving = false;
			}.bind(this), function(response)
			{
				this.lastResponse = response;
				this.moving = false;
			}.bind(this));
	}
}

Romie.prototype.left = function()
{
	if ( ! this.moving)
	{
		this.moving = true;
		Weblab.sendCommand("L",
			function(response)
			{
				this.lastResponse = response;
				this.moving = false;
			}.bind(this),
			function(response)
			{
				this.lastResponse = response;
				this.moving = false;
			}.bind(this));
	}
}

Romie.prototype.right = function()
{
	if ( ! this.moving)
	{
		this.moving = true;
		Weblab.sendCommand("R",
			function(response)
			{
				this.lastResponse = response;
				this.moving = false;
			}.bind(this),
			function(response)
			{
				this.lastResponse = response;
				this.moving = false;
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

Romie.prototype.isMoving = function()
{
	return this.moving;
}
