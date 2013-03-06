
var test_version = "v3";


function include(filename)
{
    var head = document.getElementsByTagName('head')[0];

    var script = document.createElement('script');
    script.src = filename;
    script.type = 'text/javascript';

    head.appendChild(script)
}


//include('http://mrdoob.github.com/three.js/build/three.min.js');


parent.wl_inst.handleCommandResponse = function(msg, id)
{
	alert("On command response: " + msg);
}

parent.wl_inst.handleCommandError = function(msg, id)
{
	alert("On handleCommandError: " + msg);
}

parent.wl_inst.setTime = function(time)
{
	alert("On set time" + time);
}

parent.wl_inst.startInteraction = function()
{
	alert("OnStartInteraction");
}

parent.wl_inst.end = function()
{
	alert("OnEnd");
}


function gfxinit()
{
}
