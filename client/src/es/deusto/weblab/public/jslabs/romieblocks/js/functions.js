Romie = function() {
	this.moving = false;
}

Romie.prototype.forward = function() {
	this.moving = true;
	Weblab.sendCommand('{"command":"F"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.left = function() {
	this.moving = true;
	Weblab.sendCommand('{"command":"L"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.right = function() {
	this.moving = true;
	Weblab.sendCommand('{"command":"R"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.isMoving = function() {
	return this.moving;
}

var romie = new Romie();
