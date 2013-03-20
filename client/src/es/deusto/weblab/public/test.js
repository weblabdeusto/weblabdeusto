
var test_version = "v3";




function include(filename)
{
    var head = document.getElementsByTagName('head')[0];

    var script = document.createElement('script');
    script.src = filename;
    script.type = 'text/javascript';

    head.appendChild(script)
}


//include('jslib/three.min.js');

var wl_inst = {}

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
	gfxinit();
}

parent.wl_inst.end = function()
{
	alert("OnEnd");
}

parent.wl_inst.handleFileResponse = function(msg, id)
{
	alert("On handle file response: " + msg);
}

parent.wl_inst.handleFileError = function(msg, id)
{
	alert("On handle file error: " + msg);
}

function gfxtest()
{
	alert("Test2");
}

function gfxinit2()
{
	camera = new THREE.Persssspectives( 2 );
}


function gfxinit()
{
	container = document.createElement('div');
	document.body.appendChild(container);
	
	camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innertHeight, 1, 10000);
	camera.position.z = 1000;
	
	scene = new THREE.Scene();
	
	scene.add(camera);
	
	renderer = new THREE.CanvasRenderer();
	renderer.setSize(window.innerWidth, window.innerHeight);
	
	container.appendChild(renderer.domElement);
	
	stats = new Stats();
	stats.domElement.style.position = 'absolute';
	stats.domElement.style.top = '0px';
	container.appendChild( stats.domElement );
}

function gfxanimate()
{
	requestAnimationFrame(gfxanimate);
	
	gfxrender();
	stats.update();
}

function gfxrender()
{
	renderer.autoClear = false;
	renderer.clear();
	
	renderer.render(scene, camera);
}

//@ sourceURL=test.js
