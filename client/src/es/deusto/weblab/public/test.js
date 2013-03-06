
var test_version = "v3";


function include(filename)
{
    var head = document.getElementsByTagName('head')[0];

    var script = document.createElement('script');
    script.src = filename;
    script.type = 'text/javascript';

    head.appendChild(script)
}


include('http://mrdoob.github.com/three.js/build/three.min.js');


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

function gfxtest()
{
	alert("Test");
}


function gfxinit()
{
	container = document.createElement('div');
	document.body.appendChild(container);
	
	camera = new THREE.PesrpectiveCamera( 45, window.innerWidth / window.innertHeight, 1, 10000);
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

//@ sourceURL=dynamicScript.js
