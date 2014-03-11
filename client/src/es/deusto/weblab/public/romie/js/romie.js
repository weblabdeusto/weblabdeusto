Romie = function()
{
	// TODO
}

Romie.prototype.forward = function()
{
	Weblab.sendCommand("F",
		function(response){console.log(response);},
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