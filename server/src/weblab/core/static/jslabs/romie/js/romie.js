Romie = function()
{
	this.moving = false;
}

Romie.prototype.forward = function(callback)
{
	if ( ! this.moving)
	{
		this.moving = true;
		weblab.sendCommand("F")
            .done(function(response) {
                if (response != 'OK') callback(JSON.parse(response));
                this.moving = false;
            }.bind(this));
	}
}

Romie.prototype.left = function()
{
	if ( ! this.moving)
	{
		this.moving = true;
		weblab.sendCommand("L")
            .done(function(response) {
                this.moving = false;
            }.bind(this));
	}
}

Romie.prototype.right = function()
{
	if ( ! this.moving)
	{
		this.moving = true;
		weblab.sendCommand("R")
            .done(function(response) {
                this.moving = false;
            }.bind(this));
	}
}

Romie.prototype.isMoving = function() {return this.moving;}
