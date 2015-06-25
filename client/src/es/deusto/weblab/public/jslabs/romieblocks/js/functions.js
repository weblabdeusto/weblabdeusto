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
