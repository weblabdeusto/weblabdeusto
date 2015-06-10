start_experiment = function() {
	$(parent.document).find('iframe[name=wlframe]').show();
}

Romie = function()
{
	this.moving = false;
}

Romie.prototype.forward = function() {
	console.log("FORWARD!! :D ^^")
	this.moving = true;
	Weblab.sendCommand('{"command":"F"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.left = function()
{
	console.log("LEFT!! :D ^^")
	this.moving = true;
	Weblab.sendCommand('{"command":"L"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.right = function()
{
	console.log("RIGHT!! :D ^^")
	this.moving = true;
	Weblab.sendCommand('{"command":"R"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.isMoving = function() {
	return this.moving;
}
