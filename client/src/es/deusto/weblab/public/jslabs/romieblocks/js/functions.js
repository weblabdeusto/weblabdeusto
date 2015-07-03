Romie = function() {
	this.moving = false;
	this.checking = false;
	this.lastWallCheck = null;
}

Romie.prototype.forward = function() {
	this.moving = true;
	this.lastWallCheck = null;
	Weblab.sendCommand('{"command":"F"}', function(response) {
		response = JSON.parse(response); // TODO set tag
		this.moving = false;
	}.bind(this));
}

Romie.prototype.left = function() {
	this.moving = true;
	this.lastWallCheck = null;
	Weblab.sendCommand('{"command":"L"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.right = function() {
	this.moving = true;
	this.lastWallCheck = null;
	Weblab.sendCommand('{"command":"R"}', function(response) {
		this.moving = false;
	}.bind(this));
}

Romie.prototype.checkWall = function() {
	this.checking = true;
	Weblab.sendCommand('{"command":"S"}', function(response) {
		response = JSON.parse(response);
		this.lastWallCheck = response['response'];
		this.checking = false;
	}.bind(this));
}

Romie.prototype.isMoving = function() {
	return this.moving;
}

Romie.prototype.isCheckingWall = function() {
	return this.checking;
}

Romie.prototype.isLastWallCheck = function() {
	return this.lastWallCheck;
}

// Cameras
updateTop = function() {
	d = new Date();
	$('#topCam img').attr("src", "https://cams.weblab.deusto.es/webcam/proxied.py/romie_top?"+d.getTime());
}

updateOnboard = function() {
	d = new Date();
	$('#onboardCam img').attr("src", "https://cams.weblab.deusto.es/webcam/proxied.py/romie_onboard?"+d.getTime());
}

showCameras = function() {
	$('#cams').show();
	$('#topCam img').on("load", function(){setTimeout(updateTop, 400)});
	$('#onboardCam img').on("load", function(){setTimeout(updateOnboard, 400)});
	updateTop();
	updateOnboard();
}
