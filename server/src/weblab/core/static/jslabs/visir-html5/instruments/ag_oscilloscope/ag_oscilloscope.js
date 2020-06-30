/*global trace, extend */
/*jshint laxcomma:true, multistr:true */

"use strict";
var visir = visir || {};

visir.AgilentOscilloscope = function(id, elem, props)
{
	var me = this;
	visir.AgilentOscilloscope.parent.constructor.apply(this, arguments);
	this._measureCount = 0;

	var options = $.extend({
		MeasureCalling: function() {
			me._measureCount++;
			if (me._extService) me._extService.MakeMeasurement();
		}
		,CheckToContinueCalling: function() {
			//if (me._extService) return me._extService.CanContinueMeasuring();
			var maxMeasureCount = visir.Config.Get("maxOscMeasureCount");
			if (maxMeasureCount == undefined || maxMeasureCount == null) {
				maxMeasureCount = 10;
			}
 			if (me._measureCount >= maxMeasureCount)
				return false;

			return visir.Config.Get("oscRunnable") && me._canContinueMeasuring;
		}
	}, props || {});
	this._options = options;

	this._voltages = [5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001];
	this._voltIdx = [2,2];

	this._timedivs = [0.005, 0.002, 0.001, 0.0005, 0.0002, 0.0001, 0.00005, 0.00002, 0.00001, 0.000005, 0.000002, 0.000001, 0.0000005];
	this._timeIdx = 1;

	this._triggerModes = ["autolevel", "auto", "normal"];
	this._triggerModesDisplay = ["Auto Level", "Auto", "Normal"];
	this._triggerModesLight = ["Level", "Auto", "Trig'd"];
	this._triggerModeIdx = 0;
	this._triggerLevelUnclamped = 0.0;

	var me = this;
	this._$elem = elem;

	// extend the channel information from base class with local per channel settings
	this._channels[0].visible = true;
	this._channels[0].display_offset = 0.0;
	this._channels[0].inverted = false;
	this._channels[1].visible = true;
	this._channels[1].display_offset = 0.0;
	this._channels[1].inverted = false;
	this._channels[1].xyg = false;

	this._math = { visible: false, display_offset: 0.0, method: "sub", sourceCh: 0 };

	this._cursors = { visible: false, sourceCh: 0, p1: { x: 0.004, y: 0.002 }, p2: { x: -0.004, y: -0.002 }, selected: 0 };

	this._extService = null;
	this._canContinueMeasuring = false;

	this._menuPrev = null;
	this._menuTimer = null;


	$("body").on("working", function(e) {
		if (!e.isWorking) {
			me._canContinueMeasuring =  e.shouldContinue;
			if (!e.shouldContinue) {
				me._isMeasuringContinuous = false;
				me._UpdateRunStopSingleButtons("stopped");
			}
		}
	});

	function NewMeasInfo(display, str, unit, proto) {
		return { display: display, str: str, unit: unit, proto: proto };
	}

	this._measurementInfo = [
		NewMeasInfo("Amplitude", "Ampl", "V", "voltageamplitude")
		, NewMeasInfo("Average", "Avg", "V", "voltageaverage")
		, NewMeasInfo("Base", "Base", "V", "voltagebase")
		, NewMeasInfo("Duty Cycle", "Duty", "%", "negativedutycycle")
		, NewMeasInfo("Fall Time", "Fall", "s", "falltime")

		, NewMeasInfo("Frequency", "Freq", "Hz", "frequency")
		, NewMeasInfo("Maximum", "Max", "V", "voltagemax")
		, NewMeasInfo("Minimum", "Min", "V", "voltagemin")
		, NewMeasInfo("Overshoot", "Over", "%", "overshoot")
		, NewMeasInfo("Peak-Peak", "Pk-Pk", "V", "voltagepeaktopeak")

		, NewMeasInfo("Period", "Period", "s", "period")
		, NewMeasInfo("Phase", "Phase", "deg", "phasedelay")
		, NewMeasInfo("Preshoot", "Pre", "%", "preshoot")
		, NewMeasInfo("Rise Time", "Rise", "s", "risetime")
		, NewMeasInfo("RMS", "RMS", "V", "voltagerms")

		, NewMeasInfo("Top", "Top", "V", "voltagetop")
		, NewMeasInfo("+ Width", "+Width", "s", "positivewidth")
		, NewMeasInfo("- Width", "-Width", "s", "negativewidth")
	];

	this._measurementActiveCh = 1;
	this._measurementSelectionIdx = 0;
	this._measurementsVisible = false;

	this._activeMenu = ""; // the current menu displayed
	this._activeMenuHandler = null;

	this._activeIndicator = null;
	this._menuTitleTimer = null;

	//this._isMeasuring = false;
	this._isMeasuringContinuous = false;

	var imgbase = "instruments/ag_oscilloscope/images";
	if (visir.BaseLocation) imgbase = visir.BaseLocation + imgbase;

	var tplLocation = "instruments/ag_oscilloscope/ag_oscilloscope.tpl";
	if (visir.BaseLocation) tplLocation = visir.BaseLocation + tplLocation;

	if (visir.Config.Get("cacheBuster") != null) {
		tplLocation = tplLocation + "?cacheBuster=" + visir.Config.Get("cacheBuster");
	}

	// the placeholder is only used while loading, so that size computations are done right
	var $placeholder = $('<div class="ag_osc" />');
	elem.append($placeholder);

	$.get(tplLocation, function(tpl) {
		$placeholder.remove();
		tpl = tpl.replace(/%img%/g, imgbase);
		tpl = tpl.replace(/%downloadManual%/g, visir.Lang.GetMessage("down_man"));
		elem.append(tpl);

		if (typeof G_vmlCanvasManager !== "undefined")
		{
			G_vmlCanvasManager.initElement(elem.find(".grid"));
			G_vmlCanvasManager.initElement(elem.find(".plot"));
		}

		var unitstring_tpl = '<div class="large strings visible">V</div><div class="small strings"><div class="top">m</div><div class="bottom">v</div></div>';
		elem.find(".unitstring").append(unitstring_tpl);
		elem.find(".timescale .bottom").text("s");
		elem.find(".trig_delay .bottom").text("s");
		elem.find(".trig_delay .large").text("s");

		var prev = 0;

		function newHandleFunc(up, down)
		{
			up = up || function() {};
			down = down || function() {};
			return function(elem, deg, newTouch) {
				if (newTouch) { prev = deg; }
				var diff = deg - prev;
				// fixup the wrapping
				if (diff > 180) { diff = -360 + diff; }
				else if (diff < -180) { diff = 360 + diff; }

				if (Math.abs(diff) > 360/10) {
					prev = deg;
					if (diff < 0) { down(); }
					else if (diff > 0) { up(); }
					elem.find("img").toggleClass("active");
				}
				// dont return, we want it undefined
			};
		}

		if(!visir.Config.Get("readOnly"))
		{
			// abuses the turnable to get events, but not turning the component at all
			elem.find(".offset_ch1").turnable({turn: newHandleFunc(function() { me._StepDisplayOffset(0, true); }, function() { me._StepDisplayOffset(0, false); }) });
			elem.find(".offset_ch2").turnable({turn: newHandleFunc(function() { me._StepDisplayOffset(1, true); }, function() { me._StepDisplayOffset(1, false); }) });

			elem.find(".offset_trg").turnable({turn: newHandleFunc(function() { me._StepTriggerLevel(true); }, function() { me._StepTriggerLevel(false); }) });
			elem.find(".horz").turnable({turn: newHandleFunc(function() { me._SetTimedivIdx(me._timeIdx+1); }, function() { me._SetTimedivIdx(me._timeIdx-1); }) });
			elem.find(".horz_offset").turnable({turn: newHandleFunc(function() { me._StepTriggerDelay(true); }, function() { me._StepTriggerDelay(false); }) });
			elem.find(".selection_knob").turnable({turn: newHandleFunc(function() { me._StepSelection(true); }, function() { me._StepSelection(false); }) });
			elem.find(".vert_ch1").turnable({turn: newHandleFunc(function() { me._SetVoltIdx(0, me._voltIdx[0]+1); }, function() { me._SetVoltIdx(0, me._voltIdx[0]-1);}) });
			elem.find(".vert_ch2").turnable({turn: newHandleFunc(function() { me._SetVoltIdx(1, me._voltIdx[1]+1); }, function() { me._SetVoltIdx(1, me._voltIdx[1]-1);}) });

			elem.find(".button").updownButton();
			elem.find(".channel_1").click( function() {
				// XXX: only toggle if its the active selection.. but we have no menus right now
				me._ToggleChEnabled(0);
			});
			elem.find(".channel_2").click( function() {
				// XXX: only toggle if its the active selection.. but we have no menus right now
				me._ToggleChEnabled(1);
			});

			elem.find(".button.edge").click( function() {
				// light up the edge button
				me._$elem.find(".multibutton.edge .state").removeClass("visible");
				me._$elem.find(".multibutton.edge .state.light").addClass("visible");

				me._ShowMenu("menu_edge");
			});

			elem.find(".button.cursors").click( function() {
				me._ToggleCursors();
			});

			elem.find(".button.measure").click( function() {
				me._ToggleMeasurements();
			});

			elem.find(".button.modecoupling").click( function() {
				me._ShowMenu("menu_modecoupling");
			});

			elem.find(".button.saverecall").click( function() {
				me._SaveWaveform();
			});			

			elem.find(".button.math").click( function() {
				me._ToggleMathEnabled();
			});

			elem.find(".button.single").click( function() {
				me._MakeMeasurement("single");
			});
			elem.find(".button.runstop").click( function() {
				me._MakeMeasurement("runstop");
			});

			elem.find(".display_button_1").click( function() { me._DisplayButtonClicked(1); });
			elem.find(".display_button_2").click( function() { me._DisplayButtonClicked(2); });
			elem.find(".display_button_3").click( function() { me._DisplayButtonClicked(3); });
			elem.find(".display_button_4").click( function() { me._DisplayButtonClicked(4); });
			elem.find(".display_button_5").click( function() { me._DisplayButtonClicked(5); });
			elem.find(".display_button_6").click( function() { me._DisplayButtonClicked(6); });
		}

		elem.find(".infobar .box").hide();

		me._plotWidth = me._$elem.find(".graph").width();
		me._plotHeight = me._$elem.find(".graph").height();

		me._DrawGrid(elem.find(".grid"));
		me._DrawPlot(elem.find(".plot"));
		me._UpdateChannelDisplay(0);
		me._UpdateChannelDisplay(1);
		me._UpdateDisplay();

		me._menuHandlers = {
			'menu_channel_1': CreateChannelMenu(me, 0, me._$elem.find(".menu_channel_1"))
			, 'menu_channel_2': CreateChannelMenu(me, 1, me._$elem.find(".menu_channel_2"))
			, 'menu_edge': CreateEdgeMenu(me, me._$elem.find(".menu_edge"))
			, 'menu_modecoupling': CreateTriggerModeCouplingMenu(me, me._$elem.find(".menu_modecoupling"))
			, 'menu_measure': CreateMeasurementMenu(me, me._$elem.find(".menu_measure"))
			, 'menu_cursors': CreateCursorsMenu(me, me._$elem.find(".menu_cursors"))
			, 'menu_math': CreateMathMenu(me, me._$elem.find(".menu_math"))
		};

		me._UpdateRunStopSingleButtons("stopped");

		me._ShowCursors(false);

		if (visir.Config.Get("displayManuals") == false) {
			elem.find(".manual_link").remove();
		}
	});
};

extend(visir.AgilentOscilloscope, visir.Oscilloscope);

visir.AgilentOscilloscope.prototype._DrawGrid = function($elem)
{
	var context = $elem[0].getContext('2d');

	//context.strokeStyle = "#004000";
	context.strokeStyle = "#00ff00";
	context.lineWidth		= 0.5;
	context.beginPath();

	var len = 3.5;
	/* Get the size from the .graph element instead.
		This works around the problem where canvases get no size if a parent node has display:none.
	*/
	var w = $elem.parent().width();
	var h = $elem.parent().height()

	var xspacing = w / 10;
	var yspacing = h / 8;
	var i, x, y;

	for(i=1;i<=9;i++) {
		x = xspacing * i;
		x += 0.5;
		context.moveTo(x, 0);
		context.lineTo(x, h);
	}

	for(i=1;i<=10*5 ;i++) {
		if (i % 5 === 0) { continue; }
		x = (xspacing / 5) * i;
		x += 0.5;
		var h2 = (h / 2) + 0.5;
		context.moveTo(x, h2 - len);
		context.lineTo(x, h2 + len);
	}

	for(i=1;i<=7;i++) {
		y = yspacing * i;
		context.moveTo(0, y+0.5);
		context.lineTo(w, y+0.5);
	}

	for(i=1;i<=7*5 ;i++) {
		if (i % 4 === 0) { continue; }
		y = (yspacing / 4) * i;
		y += 0.5;
		var w2 = (w / 2);
		w2 = Math.floor(w2) + 0.5;
		context.moveTo(w2 - len, y);
		context.lineTo(w2 + len, y);
	}

	context.stroke();
};

visir.AgilentOscilloscope.prototype._DrawPlot = function($elem)
{
	var context = $elem[0].getContext('2d');
	context.strokeStyle = "#00ff00";
	context.lineWidth		= 1.2;

	/* Get the size from the .graph element instead.
		This works around the problem where canvases get no size if a parent node has display:none.
	*/
	var w = $elem.parent().width();
	var h = $elem.parent().height();
	context.clearRect(0,0, w, h);
	context.beginPath();

	var me = this;
	// local draw function
	function DrawChannel(chnr) {
		if (!me._channels[chnr].visible) { return; }
		var ch = me._channels[chnr];
		var graph = ch.graph;
		var len = graph.length;
		for(var i=0;i<len;i++) {
			var x = i*w / len;
			var y = -((graph[i] * (me._channels[chnr].inverted ? -1 : 1) / ch.range) + ch.display_offset) * (h / 8.0) + h/2;
			y+=0.5;
			if (i===0) {
				context.moveTo(x,y);
			} else {
				context.lineTo(x,y);
			}
		}
	}

	function DrawXY(chnr1, chnr2) {
		if (!me._channels[chnr2].xyg) { return; }
		var maxrange = Math.max(me._channels[1].range, me._channels[0].range);
		var graph1 = me._channels[1].graph;
		var graph2 = me._channels[0].graph;
		var len = Math.min(graph1.length, graph2.length);
		var sum = 0.0;
		for(var i=0;i<len;i++) {
			var sample = 0.0;
			var sample1 = graph1[i] * (me._channels[1].inverted ? -1 : 1);
			var sample2 = graph2[i] * (me._channels[0].inverted ? -1 : 1);
			if (me._math.visible){
				sample = sample1 - sample2;
			} else {
				sample = sample1;
			}
			var x = ((sample2 / me._channels[1].range) + me._math.display_offset) * (w / 8.0) + w/2;
			var y = -((sample / me._channels[0].range) + me._math.display_offset) * (h / 8.0) + h/2;
			y += 0.5;
			if (i===0) {
				context.moveTo(x,y);
			} else {
				context.lineTo(x,y);
			}
		}
	}

	function DrawMath() {
		if (!me._math.visible) return;
		var maxrange = Math.max(me._channels[0].range, me._channels[1].range);
		var graph1 = me._channels[0].graph;
		var graph2 = me._channels[1].graph;
		var len = Math.min(graph1.length, graph2.length);
		var sum = 0.0;
		for(var i=0;i<len;i++) {
			var sample = 0.0;
			var sample1 = graph1[i] * (me._channels[0].inverted ? -1 : 1);
		 	var sample2 = graph2[i] * (me._channels[1].inverted ? -1 : 1);
			switch(me._math.method) {
				case "sub":
					sample = sample1 - sample2;
					break;
				case "mul":
					sample = sample1 * sample2;
					break;
				case "derive":
					var g = me._channels[me._math.sourceCh].graph;
					sample = (i == 0) ? 0 : g[i] - g[i-1];
					break;
				case "integrate":
					var g = me._channels[me._math.sourceCh].graph;
					//sum = sum + (i == 0) ? 0 : (g[i] + g[i-1]) / 2.0;
					sum = sum + (g[i] / 4) ;
					sample = sum;
					break;
			}

			var x = i*w / len;
			var y = -((sample / maxrange) + me._math.display_offset) * (h / 8.0) + h/2;
			y+=0.5;
			if (i===0) {
				context.moveTo(x,y);
			} else {
				context.lineTo(x,y);
			}
		}
	}

	function transformX(x)
	{
		var timediv = me._timedivs[me._timeIdx];
		return (w / 2.0) + x / timediv * (w/10.0);
	}

	function transformY(ch, y)
	{
			return -((y * (ch.inverted ? -1 : 1) / ch.range) + ch.display_offset) * (h / 8.0) + h/2;
	}

	function DrawCursors()
	{
		function DrawCursor(x1, y1, x2, y2, color, dash) {
			if (typeof context.setLineDash == "function") context.setLineDash(dash);
			context.save(); 
			context.strokeStyle = color;
			context.beginPath();
			context.moveTo(x1+0.5, y1+0.5);
			context.lineTo(x2+0.5, y2+0.5);
			context.stroke();
			context.restore();
			if (typeof context.setLineDash == "function") context.setLineDash([0]);
		}

		var ch = me._channels[me._cursors.sourceCh];

		if (!me._cursors.visible) return;
		var selcolor = "#ffff00";
		var unselcolor = "#00ffff";
		DrawCursor(transformX(me._cursors.p1.x), 0, transformX(me._cursors.p1.x), h, me._cursors.selected & 1 ? selcolor : unselcolor, [4]);
		DrawCursor(transformX(me._cursors.p2.x), 0, transformX(me._cursors.p2.x), h, me._cursors.selected & 2 ? selcolor : unselcolor, [5]);
		DrawCursor(0, transformY(ch, me._cursors.p1.y), w, transformY(ch, me._cursors.p1.y), me._cursors.selected & 4 ? selcolor : unselcolor, [6]);
		DrawCursor(0, transformY(ch, me._cursors.p2.y), w, transformY(ch, me._cursors.p2.y), me._cursors.selected & 8 ? selcolor : unselcolor, [7]);
	}
	if (!me._channels[1].xyg) {
		DrawChannel(0);
		DrawChannel(1);
		context.stroke();
		DrawCursors();

		context.strokeStyle = "#ff0000";
		context.beginPath();
		DrawMath();
		context.stroke();
	} else {
		context.strokeStyle = "#ffff00";
		context.beginPath();
		DrawXY(0,1);
		context.stroke();
	}
};

visir.AgilentOscilloscope.prototype._SetVoltIdx = function(ch, idx)
{
	if (idx < 0) { idx = 0; }
	if (idx > this._voltages.length - 1) { idx = this._voltages.length - 1; }
	this._voltIdx[ch] = idx;

	// sets value for serialization
	this._channels[ch].range = this._voltages[idx];
	this._channels[ch].offset = this._voltages[idx] * -this._channels[ch].display_offset;

	var indicatorName = (ch === 0 ? ".voltage_ch1" : ".voltage_ch2");
	var $indicator = this._$elem.find(indicatorName);
	this._LightIndicator($indicator);
	this._UpdateTriggerLevel();
	this._UpdateDisplay();
};

visir.AgilentOscilloscope.prototype._SetTimedivIdx = function(idx)
{
	if (idx < 0) { idx = 0; }
	if (idx > this._timedivs.length - 1) { idx = this._timedivs.length - 1; }
	this._timeIdx = idx;
	this._sampleRate = 1.0 / this._timedivs[this._timeIdx]; // sets value for serialization

	var $indicator = this._$elem.find(".timediv");
	this._LightIndicator($indicator);
	this._UpdateTriggerDelay();
	this._UpdateDisplay();
};

visir.AgilentOscilloscope.prototype._StepDisplayOffset = function(ch, up)
{
	var stepsize = 0.05;
	var val = this._channels[ch].display_offset + (up ? stepsize : -stepsize);
	this._SetDisplayOffset(ch, val);
};

visir.AgilentOscilloscope.prototype._SetDisplayOffset = function(ch, offset)
{
	var stepsize = 0.05;
	offset = Math.round(offset / stepsize) * stepsize;
	this._channels[ch].display_offset = offset;

	// set values for serialization
	this._channels[ch].offset = this._voltages[this._voltIdx[ch]] * -this._channels[ch].display_offset;

	// move and update offset indicators
	var $group = this._$elem.find(".display .vertical " + (ch === 0 ? ".offset_group_ch1" : ".offset_group_ch2"));
	$group.find(".ch_offset").removeClass("visible");
	if (offset >= 4) { // show overflow indicator
		$group.find(".overflow_up").addClass("visible");
	} else if (offset <= -4) { // show underflow indicator
		$group.find(".overflow_down").addClass("visible");
	} else { // show normal indicator and move it into position
		var $indicator = $group.find(".normal");
		var h = this._plotHeight;
		var top = -offset * (h / 8.0) + h/2;
		$indicator.addClass("visible");
		$indicator.css("top", top + "px");
	}

	this._UpdateTriggerLevel();
	this._UpdateDisplay();
};

/*
	The trigger level should stay the same until its steped
	When changing the voltdiv the result should be clamped and displayed correctly, but when changing back, the level should change back as well.
*/

// Takes the unclamped value as basis, steps and sets a new value based on that.
visir.AgilentOscilloscope.prototype._StepTriggerLevel = function(up)
{
	// side effect, if trigger mode is auto level, set to auto
	if (this._triggerModeIdx === 0) {
		this._SetTriggerMode(1);
	}

	var level = this._ClampTriggerLevel(this._triggerLevelUnclamped);

	var trigch = this._channels[this._trigger.source - 1];
	var stepsize = trigch.range / 10;
	var newval = level + (up ? stepsize : -stepsize);
	this._triggerLevelUnclamped = newval;

	this._SetTriggerLevel(newval, true);
};

// clamps the trigger level, sets up the serialized data and updates the display
visir.AgilentOscilloscope.prototype._SetTriggerLevel = function(level, showLight)
{
	showLight = showLight || false;
	level = this._ClampTriggerLevel(level);

	this._trigger.level = level;

	var $indicator = this._$elem.find(".triglevel .lighttext");
	//this._$elem.find(".triglevel .lighttext").text(this._FormatValue(level) + "V");
	this._LightIndicator($indicator);
	this._UpdateTriggerLevel();
};

visir.AgilentOscilloscope.prototype._ClampTriggerLevel = function(level)
{
	var trigch = this._channels[this._trigger.source - 1];
	var stepsize = trigch.range / 10;
	level = Math.round(level / stepsize) * stepsize;
	var max = -trigch.offset + (6*trigch.range);
	var min = -trigch.offset - (6*trigch.range);
	if (level > max) { level = max; }
	if (level < min) { level = min; }
	return level;
};

visir.AgilentOscilloscope.prototype._UpdateTriggerLevel = function()
{
	var trigch = this._channels[this._trigger.source - 1];
	var level = this._ClampTriggerLevel(this._triggerLevelUnclamped);
	this._trigger.level = level; // XXX: updating the serialized value here is not optimal..

	//trace("update trigger level: " + (this._trigger.source - 1) + " " + level);

	var markerPos = (((-level + trigch.offset) / trigch.range) ) * (this._plotHeight / 8.0) + (this._plotHeight / 2.0);
	markerPos = Math.round(markerPos);

	var $group = this._$elem.find(".display .vertical .group.trigger_group");
	$group.find(".ch_offset").removeClass("visible");

	if (markerPos <= 0) { // show overflow indicator
		$group.find(".overflow_up").addClass("visible");
	} else if (markerPos >= this._plotHeight) { // show underflow indicator
		$group.find(".overflow_down").addClass("visible");
	} else { // show normal indicator and move it into position
		var $indicator = $group.find(".normal");
		$indicator.addClass("visible");
		$indicator.css("top", markerPos + "px");
	}

	this._SetIndicatorValue(this._$elem.find(".triglevel .lighttext"), level);
	//SetText(this._$elem.find(".triglevel .lighttext"), this._FormatValue(level));
	//this._$elem.find(".triglevel .lighttext").text(this._FormatValue(level));
};

/* Trigger delay */

visir.AgilentOscilloscope.prototype._ClampTriggerDelay = function(val)
{
	var timediv = this._timedivs[this._timeIdx];
	var stepsize = timediv / 10;
	val = Math.round(val / stepsize) * stepsize;
	var max = timediv * 10; //-trigch.offset + (6*trigch.range);
	var min = 0; //-trigch.offset - (6*trigch.range);
	if (val > max) { val = max; }
	if (val < min) { val = min; }
	return val;
}

visir.AgilentOscilloscope.prototype._StepTriggerDelay = function(up)
{	
	var timediv = this._timedivs[this._timeIdx];
	var stepsize = timediv / 10;
	var val = this._trigger.delay + (up ? -stepsize : stepsize);
	val = this._ClampTriggerDelay(val);
	this._trigger.delay = val;
	
	var $indicator = this._$elem.find(".trig_delay");
	this._LightIndicator($indicator);
	
	this._UpdateTriggerDelay();
	this._UpdateDisplay();
	
	//trace("_StepTriggerDelay: " + val);
}

visir.AgilentOscilloscope.prototype._UpdateTriggerDelay = function()
{
	trace("_UpdateTriggerDelay");
	var timediv = this._timedivs[this._timeIdx];
	var markerPos = ((-this._trigger.delay / timediv) ) * (this._plotWidth / 10.0) + (this._plotWidth / 2.0) - 3;
	markerPos = Math.round(markerPos);
	this._$elem.find(".timedelay_markers .marker").css("left", markerPos + "px");
	//trace("mX: " + markerPos);
}

/* */

// XXX: maybe rename to ChButtonPressed or something..
visir.AgilentOscilloscope.prototype._ToggleChEnabled = function(ch)
{
	var showMenu = "menu_channel_" + (ch+1);
	var visibile = this._activeMenu !== showMenu || !this._channels[ch].visible;
	this._ShowMenu(showMenu);
	this._SetChEnabled(ch, visibile);
};

visir.AgilentOscilloscope.prototype._ToggleMathEnabled = function()
{
	var visible = this._activeMenu !== "menu_math" || !this._math.visible;
	this._ShowMenu("menu_math");
	this._math.visible = visible;
	this._SetLightButtonState(this._$elem.find(".multibutton.math"), visible);
	this._UpdateDisplay();
}

visir.AgilentOscilloscope.prototype._ToggleChCoupling = function(ch)
{
	this._channels[ch].coupling = (this._channels[ch].coupling === "dc") ? "ac" : "dc";
};

visir.AgilentOscilloscope.prototype._SetChEnabled = function(ch, enabled)
{
	this._channels[ch].visible = enabled;
	this._UpdateChannelDisplay(ch);
	this._UpdateDisplay();
};

visir.AgilentOscilloscope.prototype._SetTriggerSlope = function(slope)
{
	this._trigger.slope = slope;
	this._$elem.find(".display .triggerslope .flank.selected").removeClass("selected");
	this._$elem.find(".display .triggerslope .flank." +slope).addClass("selected");
};

visir.AgilentOscilloscope.prototype._SetTriggerSource = function(ch)
{
	this._trigger.source = ch;
	this._$elem.find(".display .triggersource .channelname").text(ch);
	this._UpdateTriggerLevel();
};

visir.AgilentOscilloscope.prototype._SetTriggerMode = function(modeIdx)
{
	if (modeIdx < 0 || modeIdx >= this._triggerModes.length) {
		throw "invalid trigger mode index";
	}
	this._triggerModeIdx = modeIdx;
	this._trigger.mode = this._triggerModes[modeIdx];

	this._$elem.find(".lighttext.triggermode").text(this._triggerModesLight[modeIdx]);
	this._$elem.find(".menu_modecoupling .value.mode").text(this._triggerModesDisplay[this._triggerModeIdx]); // need to update the menu (if its active)
};

visir.AgilentOscilloscope.prototype._IsMeasurementEnabled = function()
{
}

visir.AgilentOscilloscope.prototype._ToggleMeasurements = function()
{
	var enabled = this._IsMeasurementEnabled();
	// if ( measurement mode is selected) {
	enabled = !enabled;
	// }
	this._ShowMenu("menu_measure");
}

visir.AgilentOscilloscope.prototype._AddMeasurementAndAnimate = function(ch, selection)
{
	// update protocol info
	var full = this._measurements.length == 3;
	var replaced = this.AddMeasurement(ch, this._measurementInfo[this._measurementSelectionIdx].proto, selection);
	var $infobar = this._$elem.find(".infobar");
	var $box1 = $infobar.find(".box1");
	var $box2 = $infobar.find(".box2");
	var $box3 = $infobar.find(".box3");

	var pos = [ 0, 110, 220];
	var fast = 250;
	var slowanim = { left: "-=110" };
	var fastanim = { left: "-=250" };

	trace("replaced: " + replaced);

	if (replaced >= 0) {
		// move first box back to second and animate back to first
		if (replaced < 1) { $box1.stop().css("left", pos[1] + "px").animate(slowanim); }
		// move second to third and animate to second
		if (replaced < 2) { $box2.stop().css("left", pos[2] + "px").animate(slowanim); }
	} else if (full) {
		// if the container is full and none were replaced, move the first and second
		$box1.show().stop().css("left", pos[1] + "px").animate(slowanim);
		$box2.show().stop().css("left", pos[2] + "px").animate(slowanim);
	}

	$box1.text("(" + this._measurements[0].channel + ") " + this._measurementInfo[this._measurements[0].extra].str + ":");
	if (this._measurements.length > 1) $box2.text("(" + this._measurements[1].channel + ") " + this._measurementInfo[this._measurements[1].extra].str + ":");
	if (this._measurements.length > 2) $box3.text("(" + this._measurements[2].channel + ") " + this._measurementInfo[this._measurements[2].extra].str + ":");

	// move in the last item with greater speed
	if (this._measurements.length == 1) { $box1.show().stop().css("left", pos[0] + fast + "px").animate(fastanim); }
	if (this._measurements.length == 2) { $box2.show().stop().css("left", pos[1] + fast + "px").animate(fastanim); }
	if (this._measurements.length == 3) { $box3.show().stop().css("left", pos[2] + fast + "px").animate(fastanim); }
}

visir.AgilentOscilloscope.prototype._ClearMeasurement = function()
{
	this._$elem.find(".infobar .box").hide();
	this._measurements = [];
}

visir.AgilentOscilloscope.prototype._StepSelection = function(up)
{
	if (this._activeMenu == "menu_measure") {
		this._measurementSelectionIdx = (up) ? this._measurementSelectionIdx + 1 : this._measurementSelectionIdx - 1;
		if (this._measurementSelectionIdx < 0) this._measurementSelectionIdx = this._measurementInfo.length - 1;
		if (this._measurementSelectionIdx >= this._measurementInfo.length) this._measurementSelectionIdx = 0;
		this._activeMenuHandler.ShowMenu("sel_meas_selection");
	}
}

visir.AgilentOscilloscope.prototype._ShowMenu = function(menuname)
{
	var $menu = this._$elem.find(".menu." + menuname);
	if ($menu.length === 0) {
		throw "unable to find menu: " + menuname;
	}
	this._$elem.find(".display .menubar .menu").removeClass("visible");
	$menu.addClass("visible");

	this._activeMenu = menuname;
	this._activeMenuHandler = this._menuHandlers[menuname];
	var name = this._activeMenuHandler.GetName();
	this._$elem.find(".display .menubar .menutitle .titlebox").text(name);
	this._$elem.find(".display .menubar .menutitle").addClass("visible");

	if (this._menuTitleTimer) {
		clearTimeout(this._menuTitleTimer);
	}
	var me = this;
	this._menuTitleTimer = setTimeout( function() { me._$elem.find(".display .menubar .menutitle").removeClass("visible"); this._menuTitleTimer = null; }, 1000);
};

visir.AgilentOscilloscope.prototype._DisplayButtonClicked = function(button)
{
	if (this._activeMenuHandler && this._activeMenuHandler.ButtonPressed) {
		this._activeMenuHandler.ButtonPressed(button);
	}
};

visir.AgilentOscilloscope.prototype._GetUnit = function(val)
{
	var units = [
		["M", 6 ]
		, ["K", 3 ]
		, ["", 0]
		, ["m", -3]
		, ["u", -6]
		, ["n", -9]
		];
	val = Math.abs(val);
	if (val === 0) {
		return { unit: "", pow: 0 };
	}

	for (var key in units) {
		var unit = units[key];
		if (val >= Math.pow(10, unit[1])) {
			return {unit: unit[0], pow: unit[1] };
		}
	}

	var last = units[units.length - 1];
	return {unit: last[0], pow: last[1] };
};

// takes care of updating the light indicator value and sets the unit string correctly if present
visir.AgilentOscilloscope.prototype._SetIndicatorValue = function($elem, value)
{
	var unit = this._GetUnit(value);
	value /= Math.pow(10,unit.pow);
	var str = value.toPrecision(3);

	$elem.find(".strings").removeClass("visible");
	$elem.find((unit.unit === "") ? ".large" : ".small").addClass("visible");
	$elem.find(".top").text(unit.unit);
	$elem.find(".value").text(this._FormatValue(str));
	//SetText($elem, this._FormatValue(str));
};

visir.AgilentOscilloscope.prototype._LightIndicator = function($elem)
{
	if (this._activeIndicator && this._activeIndicator.Destroy) {
		this._activeIndicator.Destroy();
		this._activeIndicator = null;
	}

	var me = this;
	$elem.addClass("light");
	var timer = setTimeout(function() {
		me._activeIndicator.Destroy();
		me._activeIndicator = null;
	}, 2000);

	this._activeIndicator = {
		Destroy: function() { $elem.removeClass("light"); clearInterval(timer); }
	};
};

visir.AgilentOscilloscope.prototype._FormatValue = function(val)
{
	var unit = this._GetUnit(val);
	val /= Math.pow(10,unit.pow);
	return val.toPrecision(3) + unit.unit;
};

visir.AgilentOscilloscope.prototype._SetLightButtonState = function($btn, lightOn)
{
	$btn.find(".state").removeClass("visible");
	if (lightOn) {
		$btn.find(".light").addClass("visible");
	} else {
		$btn.find(".dark").addClass("visible");
	}
}

// this should be called when the channel properties have changed
// currently: visible is tracked
visir.AgilentOscilloscope.prototype._UpdateChannelDisplay = function(ch)
{
		var css_ch_name = ".channel." + (ch===0 ? "ch1" : "ch2");
		var css_group_name = ".display .vertical .offset_group_" + (ch===0 ? "ch1" : "ch2");
		var css_button_name = ".multibutton.channel_" + (ch+1);
		if (this._channels[ch].visible) {
			this._$elem.find(css_ch_name).addClass("visible");
			this._$elem.find(css_group_name).addClass("visible");
			this._$elem.find(css_button_name).find(".state").removeClass("visible");
			this._$elem.find(css_button_name).find(".light").addClass("visible");
		} else {
			this._$elem.find(css_ch_name).removeClass("visible");
			this._$elem.find(css_group_name).removeClass("visible");
			this._$elem.find(css_button_name).find(".state").removeClass("visible");
			this._$elem.find(css_button_name).find(".dark").addClass("visible");
		}
};

visir.AgilentOscilloscope.prototype._UpdateDisplay = function()
{
	this._SetIndicatorValue(this._$elem.find(".voltage_ch1"), this._voltages[this._voltIdx[0]]);
	this._SetIndicatorValue(this._$elem.find(".voltage_ch2"), this._voltages[this._voltIdx[1]]);
	this._SetIndicatorValue(this._$elem.find(".timediv"), this._timedivs[this._timeIdx]);
	this._SetIndicatorValue(this._$elem.find(".topbar .trig_delay"), this._trigger.delay);
	//this._$elem.find(".voltage_ch1").text(this._FormatValue(this._voltages[this._voltIdx[0]]) + "V");
	//this._$elem.find(".voltage_ch2").text(this._FormatValue(this._voltages[this._voltIdx[1]]) + "V");
	//this._$elem.find(".timediv").text(this._FormatValue(this._timedivs[this._timeIdx]) + "s");

	this._DrawPlot(this._$elem.find(".plot"));
};

visir.AgilentOscilloscope.prototype._ToggleCursors = function()
{

}

visir.AgilentOscilloscope.prototype._ShowCursors = function(show)
{
	this._$elem.find(".graph .cursors").toggle(show);

	var $infobar = this._$elem.find(".infobar");
	var $box1 = $infobar.find(".box1");
	var $box2 = $infobar.find(".box2");
	var $box3 = $infobar.find(".box3");
	$box1.toggle(show);
	$box2.toggle(show);
	$box3.toggle(show);
}

visir.AgilentOscilloscope.prototype.ReadResponse = function(response) {
	var me = this;
	visir.AgilentOscilloscope.parent.ReadResponse.apply(this, arguments);
	this._DrawPlot(this._$elem.find(".plot"));

	// check if we should continue measuring
	if (this._isMeasuringContinuous && this._options.CheckToContinueCalling()) {
		this._options.MeasureCalling();
	} else {
		this._isMeasuringContinuous = false;
		this._$elem.find(".button.runstop .state").removeClass("visible");
		this._$elem.find(".button.runstop .state.red").addClass("visible");
		this._$elem.find(".button.single .state").removeClass("visible");
		this._$elem.find(".button.single .state.dark").addClass("visible");
	}

	function UpdateResult($elem, measurement) {
		var str = "(" + measurement.channel + ") " + me._measurementInfo[measurement.extra].str + ": ";
		var unit = visir.GetUnit(measurement.result);
		str += (measurement.result / Math.pow(10, unit.pow)).toPrecision(4);
		str += unit.unit;
		str += me._measurementInfo[measurement.extra].unit;
		$elem.text(str);
	}

	var $measurements = this._$elem.find(".measurements");
	if (this._measurements.length > 0) UpdateResult($measurements.find(".box1"), this._measurements[0]);
	if (this._measurements.length > 1) UpdateResult($measurements.find(".box2"), this._measurements[1]);
	if (this._measurements.length > 2) UpdateResult($measurements.find(".box3"), this._measurements[2]);
};

visir.AgilentOscilloscope.prototype._UpdateRunStopSingleButtons = function(state)
{
	switch(state) {
		case "single":
			this._$elem.find(".button.runstop .state").removeClass("visible");
			this._$elem.find(".button.runstop .state.dark").addClass("visible");
			this._$elem.find(".button.single .state").removeClass("visible");
			this._$elem.find(".button.single .state.light").addClass("visible");
		break;

		case "run":
			this._$elem.find(".button.single .state").removeClass("visible");
			this._$elem.find(".button.single .state.dark").addClass("visible");
			this._$elem.find(".button.runstop .state").removeClass("visible");
			this._$elem.find(".button.runstop .state.green").addClass("visible");
		break;

		case "stopped":
		default:
			this._$elem.find(".button.runstop .state").removeClass("visible");
			this._$elem.find(".button.runstop .state.red").addClass("visible");
			this._$elem.find(".button.single .state").removeClass("visible");
			this._$elem.find(".button.single .state.dark").addClass("visible");
		break;
	}
}

visir.AgilentOscilloscope.prototype._MakeMeasurement = function(button) {
	this._measureCount = 0;
	switch(button) {
		case "single":
			this._UpdateRunStopSingleButtons("single");
			this._isMeasuringContinuous = false;
			this._options.MeasureCalling();

		break;
		case "runstop":
			this._UpdateRunStopSingleButtons("run");
			if ( ! visir.Config.Get("oscRunnable") || this._isMeasuringContinuous) {
				this._isMeasuringContinuous = false;
				this._UpdateRunStopSingleButtons("stopped");

				if ( ! visir.Config.Get("oscRunnable"))
					alert(visir.Lang.GetMessage("osc_not_runnable"));
			} else {
				this._isMeasuringContinuous = true;
				this._options.MeasureCalling();
			}
		break;
	}
};

visir.AgilentOscilloscope.prototype.UseExteralService = function(service) {
	trace("AgilentOscilloscope::UseExteralService");
	this._extService = service;
}

visir.AgilentOscilloscope.prototype._HideMenuAfter = function(menu, unique, duration_ms) {
	duration_ms = duration_ms || 1000;
	unique = unique || 1;

	//var same = menu === this._menuPrev;

	var me = this;
	var hideFunc = function() { menu.HideMenu(unique); me._menuPrev = null; trace("---------- hiding ---------");}

	var same = (!!this._menuPrev) && (this._menuPrev.menu === menu) && (this._menuPrev.unique == unique);
	trace("prevmenu: " + this._menuPrev);

	if (!same && this._menuPrev) {
		trace("hiding previous");
		this._menuPrev.hideFunc();
	}

	if (this._menuTimer) {
		trace("clear timer");
		clearTimeout(this._menuTimer);
	}
	
	this._menuTimer = setTimeout(hideFunc, duration_ms); 
	this._menuPrev = { menu: menu, unique: unique, hideFunc: hideFunc };

	trace("same: " + same);
	return same;
}

visir.AgilentOscilloscope.prototype._SaveWaveform = function() {
	trace("Saving waveform to csv");

	if (navigator.userAgent.match(/iPhone|iPad|Android/)) {
		trace("Save not supported on handheld devices");
		return;
	}

	var out = '';
	out += 'sep=\t\r\n';
	out += 'Time\tChannel1\tChannel2\r\n';

	var ch1 = this._channels[0].graph;
	var ch2 = this._channels[1].graph;
	var dtime1 = this._timedivs[this._timeIdx] * 10.0 / this._channels[0].graph.length;
	for(var i=0;i<ch1.length;i++) {
		var t1 = (i - (ch1.length / 2)) * dtime1;
		out += t1 + "\t" + ch1[i] + "\t" + ch2[i] + "\r\n";
	}

	var blob = new Blob([out], {type: "text/csv;charset=UTF-8"});
	saveAs(blob, "waveform.csv");
}

/* Menus */

function CreateChannelMenu(osc, ch, $menu)
{
	var timer = null;
	return {
		GetName: function() { this.Redraw(); return "Channel " + (ch+1) + " Menu"; },
		ButtonPressed: function(nr) {
			switch(nr) {
				case 1:
					if (!this.ShowMenu()) return;
					osc._ToggleChCoupling(ch);
					this.Redraw();
				break;
				case 2:
					osc._channels[ch].inverted = !osc._channels[ch].inverted;
					this.Redraw();
					osc._UpdateDisplay();
					break;
				case 3:
					if (ch == 1) {
						osc._channels[ch].xyg = !osc._channels[ch].xyg;
						this.Redraw();
						osc._UpdateDisplay();
					}
				default:
				break;
			}

		},
		Redraw: function() {
			var coupling = osc._channels[ch].coupling;
			$menu.find(".value.coupling").text(coupling.toUpperCase());
			$menu.find(".selection").removeClass("selected");
			$menu.find(".selection.sel_" + coupling).addClass("selected");
			$menu.find(".checkbox.invert").removeClass("selected");
			$menu.find(".checkbox.xyg").removeClass("selected");
			if(osc._channels[ch].inverted) {
				$menu.find(".checkbox.invert").addClass("selected");
			}
			if(osc._channels[ch].xyg) {
				$menu.find(".checkbox.xyg").addClass("selected");
			}
		},
		ShowMenu: function() {
			$menu.find(".menu_selection.sel_ch_" + (ch+1)).addClass("visible");
			return osc._HideMenuAfter(this);
		},
		HideMenu: function() {
			$menu.find(".menu_selection.sel_ch_" + (ch+1)).removeClass("visible");
		}
	};
}

function CreateEdgeMenu(osc, $menu)
{
	return {
		GetName: function() { return "Edge Menu"; },
		ButtonPressed: function(nr) {
			switch(nr) {
				case 1:
					// move this to function, we need to update other stuff
					osc._SetTriggerSlope((osc._trigger.slope === "positive") ? "negative" : "positive");
				break;
				case 2:
					osc._SetTriggerSource(1);
				break;
				case 3:
					osc._SetTriggerSource(2);
				break;
			}
			this.Redraw();
		},
		Redraw: function() {
			$menu.find(".edgeselect.selected").removeClass("selected");
			$menu.find(".edgeselect." + osc._trigger.slope).addClass("selected");
			$menu.find(".menubox .value .checkmark").removeClass("selected");
			$menu.find(".menubox .value .checkmark.ch"+ osc._trigger.source).addClass("selected");
		}
	};
}

function CreateTriggerModeCouplingMenu(osc, $menu)
{
	var timer = null;
	return {
		GetName: function() { this.Redraw(); return "Mode / Coupling Menu"; },
		ButtonPressed: function(nr) {
			this.Redraw();
			switch(nr) {
				case 1:
					if (!this.ShowMenu("sel_trigger_mode")) { return; }
					var tmp = osc._triggerModeIdx + 1;
					if (tmp >= osc._triggerModes.length) { tmp = 0; }
					osc._SetTriggerMode(tmp);
				break;
				case 2:
					if (!this.ShowMenu("sel_trigger_coupling")) { return; }
					osc._trigger.coupling = (osc._trigger.coupling === "dc") ? "ac" : "dc";
				break;
			}
			this.Redraw();
		},
		Redraw: function() {
			$menu.find(".selection").removeClass("selected");
			$menu.find(".sel_trigger_mode .sel_" + osc._triggerModes[osc._triggerModeIdx]).addClass("selected");
			$menu.find(".sel_trigger_coupling .sel_" + osc._trigger.coupling).addClass("selected");
			$menu.find(".value.coupling").text(osc._trigger.coupling.toUpperCase());
			$menu.find(".value.mode").text(osc._triggerModesDisplay[osc._triggerModeIdx]);
		},
		ShowMenu: function(name) {
			this.HideMenu();
			$menu.find(".menu_selection." + name).addClass("visible");
			var menu = this;
			if (!timer) {
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return false;
			} else {
				clearInterval(timer);
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return true;
			}
		},
		HideMenu: function() {
			$menu.find(".menu_selection").removeClass("visible");
		}
	};
}

function CreateMeasurementMenu(osc, $menu)
{
	var timer = null;

	var $sel = $menu.find(".sel_meas_selection");
	for(var i=0;i < osc._measurementInfo.length; i++) {
		var $row = $('<div class="selection"><div class="checkmark_holder"><div class="checkmark" /></div><span>' + osc._measurementInfo[i].display + '</span></div>');
		$sel.append($row);
	}

	//$sel.find(".selection").first().addClass("selected");
	$sel.find(":nth-child(3)").addClass("selected");

	return {
		GetName: function() { this.Redraw(); return "Measurement Menu"; },
		ButtonPressed: function(nr) {
			this.Redraw();
			switch(nr) {
				case 1:
					if (!this.ShowMenu("sel_meas_source")) return;
					osc._measurementActiveCh = (osc._measurementActiveCh == 1) ? 2 : 1;
				break;
				case 2:
					if (!this.ShowMenu("sel_meas_selection")) return false;
					osc._measurementSelectionIdx++;
					if (osc._measurementSelectionIdx >= osc._measurementInfo.length) osc._measurementSelectionIdx = 0;
				break;

				case 3:
					osc._AddMeasurementAndAnimate(osc._measurementActiveCh, osc._measurementSelectionIdx);
				break;

				case 4:
					osc._ClearMeasurement();
				break;
			}
			this.Redraw();
		},
		Redraw: function() {
			$menu.find(".selection").removeClass("selected");
			$menu.find(".sel_meas_source .sel_" + osc._measurementActiveCh).addClass("selected");
			$menu.find(".sel_meas_selection .selection:nth-child(" + (3 + osc._measurementSelectionIdx) + ")").addClass("selected");
			$menu.find(".value.selection").text(osc._measurementInfo[osc._measurementSelectionIdx].str);
			$menu.find(".value.measure").text(osc._measurementInfo[osc._measurementSelectionIdx].str);
			$menu.find(".value.source").text(osc._measurementActiveCh);
		},
		ShowMenu: function(name) {
			this.Redraw();
			this.HideMenu();
			$menu.find(".menu_selection." + name).addClass("visible");
			var menu = this;
			if (!timer) {
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return false;
			} else {
				clearInterval(timer);
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return true;
			}
		},
		HideMenu: function() {
			$menu.find(".menu_selection").removeClass("visible");
		}
	};
}

function CreateCursorsMenu(osc, $menu)
{
	var timer = null;
	return {
		GetName: function() { this.Redraw(); return "Cursor Menu"; },
		ButtonPressed: function(nr) {
			this.Redraw();
			switch(nr) {
				case 1:
					// mode
				break;
				case 2:
					// source
				break;
				case 3:
					// x / y
				break;
				case 4:
					// xy1
				break;
				case 5:
					// xy2
				break;
				case 6:
					// xy both
				break;
			}
			this.Redraw();
		},
		Redraw: function() {
		},
		ShowMenu: function(name) {
			this.HideMenu();
			$menu.find(".menu_selection." + name).addClass("visible");
			var menu = this;
			if (!timer) {
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return false;
			} else {
				clearInterval(timer);
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return true;
			}
		},
		HideMenu: function() {
			$menu.find(".menu_selection").removeClass("visible");
		}
	};
}

function CreateMathMenu(osc, $menu)
{
	var timer = null;
	return {
		GetName: function() { this.Redraw(); return "Math Menu"; },
		ButtonPressed: function(nr) {
			switch(nr) {
				case 1:
				break;
				case 2:
				break;
				case 3:
					osc._math.method = "mul";
				break;
				case 4:
					osc._math.method = "sub";
				break;
				case 5:
					//osc._math.method = "derive";
				break;
				case 6:
					//osc._math.method = "integrate";
				break;
			}
			this.Redraw();
			osc._UpdateDisplay();
		},
		Redraw: function() {
			$menu.find(".menubox .value .checkmark").removeClass("selected");
			$menu.find(".menubox .value .checkmark."+ osc._math.method).addClass("selected");
		},
		ShowMenu: function(name) {
			this.HideMenu();
			$menu.find(".menu_selection." + name).addClass("visible");
			var menu = this;
			if (!timer) {
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return false;
			} else {
				clearInterval(timer);
				timer = setTimeout(function() { timer=null; menu.HideMenu(); }, 1000);
				return true;
			}
		},
		HideMenu: function() {
			$menu.find(".menu_selection").removeClass("visible");
		}
	};
}


