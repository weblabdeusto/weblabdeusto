var visir = visir || {};

visir.Load = function( onSuccess, onFailure, baseurl )
{
	baseurl = baseurl || "";
	visir.BaseLocation = baseurl;
	var css = [
		"instruments/breadboard/breadboard.css"
		, "instruments/flukemultimeter/flukemultimeter.css"
		, "instruments/tripledc/tripledc.css"
		, "instruments/hp_funcgen/hp_funcgen.css"
		, "instruments/ag_oscilloscope/ag_oscilloscope.css"
		, "instruments/ni_oscilloscope/ni_oscilloscope.css"
		, "instrumentframe/instrumentframe.css"
	];

	var stage1_scripts = [
		"utils.js"
		, "services.js"
		, "jquery-turnable.js"
		, "jquery-draggable.js"
		, "jquery-updownbutton.js"
		, "config.js"
	];

	var stage2_scripts = [
		"language.js"
	];

	var stage3_scripts = [
		"instrumentregistry.js"
		, "instruments/multimeter.js"
		, "instruments/oscilloscope.js"
		, "instruments/functiongenerator.js"
		, "instruments/dcpower.js"
		, "instruments/transport.js"
	];

	var stage4_scripts = [
		"instruments/breadboard/breadboard.js"
		, "instruments/flukemultimeter/flukemultimeter.js"
		, "instruments/tripledc/tripledc.js"
		, "instruments/hp_funcgen/hp_funcgen.js"
		, "instruments/ag_oscilloscope/ag_oscilloscope.js"
		, "instruments/ni_oscilloscope/ni_oscilloscope.js"
		, "instrumentframe/instrumentframe.js"
	];

	function InjectCSS(src)
	{
		var def = $.Deferred();
		var head=document.getElementsByTagName('head')[0];
		var script=document.createElement('link');
		script.rel = "stylesheet";
		script.onreadystatechange= function () {
			if (this.readyState == 'complete') {
				//trace("readystate: " + src);
				def.resolve();
			}
		}
		script.onload = function() {
			//trace("onload: " + src);
			def.resolve();
		}
		script.href = baseurl + src;
		head.appendChild(script);
		return def.promise();
	}

	function InjectScript(src)
	{
		var def = $.Deferred();
		var head=document.getElementsByTagName('head')[0];
		var script=document.createElement('script');
		script.type= 'text/javascript';
		script.onreadystatechange= function () {
			if (this.readyState == 'complete') {
				//trace("readystate: " + src);
				def.resolve();
			}
		}
		script.onload = function() {
			//trace("onload: " + src);
			def.resolve();
		}
		script.src = baseurl + src;
		head.appendChild(script);
		return def.promise();
	}

	// we need to load the essentials dependecies before loading the rest of the files
	function GetStage1()
	{
		var defs = [];
		for(var i=0;i<stage1_scripts.length; i++) {
			defs.push( InjectScript(stage1_scripts[i]) );
		}
		return defs;
	}

	function GetStage2()
	{
		var defs = [];
		for(var i=0;i<stage2_scripts.length; i++) {
			defs.push( InjectScript(stage2_scripts[i]) );
		}
		return defs;
	}

	function GetStage3()
	{
		var defs = [];
		for(var i=0;i<stage3_scripts.length; i++) {
			defs.push( InjectScript(stage3_scripts[i]) );
		}
		return defs;
	}

	function GetStage4() {
		var defs = [];
		for(var i=0;i<stage4_scripts.length; i++) {
			defs.push( InjectScript(stage4_scripts[i]) );
		}
		for(var i=0;i<css.length; i++) {
			defs.push( InjectCSS(css[i]) );
		}
		return defs;
	}

	var deferred_1 = GetStage1();
	$.when.apply(null, deferred_1).done( function() {
		var deferred_2 = GetStage2();
	$.when.apply(null, deferred_2).done( function() {
		var deferred_3 = GetStage3();
	$.when.apply(null, deferred_3).done( function() {
		var deferred_4 = GetStage4();
	$.when.apply(null, deferred_4).done(onSuccess);
	});});})
}