/*global trace, extend */
/*jshint laxcomma:true, multistr:true */

"use strict";
var visir = visir || {};

visir.NationalInstrumentOscilloscope = function(id, elem, props)
{
	visir.NationalInstrumentOscilloscope.parent.constructor.apply(this, arguments);

	var options = $.extend({
		MeasureCalling: function() {}
		,CheckToContinueCalling: function() { return false; }
	}, props || {});
	this._options = options;

	this._voltages = [5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001];
	this._voltagesDisplay = ["5V", "2V", "1V", "0.5V", "0.2V", "0.1V", "50.0mV", "20.0mV", "10.0mV", "5.0mV", "2.0mV", "1.0mV"];
	this._voltIdx = [2,2];

	this._timedivs = [0.005, 0.002, 0.001, 0.0005, 0.0002, 0.0001, 0.00005, 0.00002, 0.00001, 0.000005, 0.000002, 0.000001, 0.0000005];
	this._timedivsDisplay = ["5.0ms", "2.0ms", "1.0ms", "0.50ms", "0.20ms", "0.10ms", "50.0us", "20.0us", "10.0us", "5.0us", "2.0us", "1.0us", "0.50us"];
	this._timeIdx = 1;

	this._triggerModeIdx = 0;
	//this._triggerLevelUnclamped = 0.0;

	this._isMeasuringContinuous = true;

	var me = this;
	this._$elem = elem;

	this._channels[0].visible = true;
	this._channels[0].display_offset = 0.0;
	this._channels[1].visible = true;
	this._channels[1].display_offset = 0.0;

	var imgbase = "instruments/ni_oscilloscope/images";
	$.get("instruments/ni_oscilloscope/ni_oscilloscope.tpl", function(tpl) {
		tpl = tpl.replace(/%img%/g, imgbase);
		elem.append(tpl);

		var $plot = elem.find(".plot");
		me._plotWidth = $plot.width();
		me._plotHeight = $plot.height();

		me._DrawGrid(elem.find(".grid"));
		me._DrawPlot(elem.find(".plot"));

		elem.find(".graph .offsetbox.ch1").draggable( {
			move: function($elem, x, y) {
				var h = $elem.parent().height();
				if (y < 0) y = 0;
				if (y > h) y = h;
				me._SetDisplayOffset(0, ((y / h) - 0.5) * -8.0);
				return {x: undefined, y: y };
			}
		});

		elem.find(".graph .offsetbox.ch2").draggable( {
			move: function($elem, x, y) {
				var h = $elem.parent().height();
				if (y < 0) y = 0;
				if (y > h) y = h;

				me._SetDisplayOffset(1, ((y / h) - 0.5) * -8.0);
				return {x: undefined, y: y };
			}
		});

		elem.find(".graph .offsetbox.trigger").draggable( {
			move: function($elem, x, y) {
				var h = $elem.parent().height();
				if (y < 0) y = 0;
				if (y > h) y = h;

				var trigch = me._channels[me._trigger.source - 1];
				var level = ((y / h) - 0.5) * -8.0;
				var trig = (((level - trigch.display_offset) * trigch.range) );

				trace("T: " + trig);

				me._SetTriggerLevel(trig);

				//me._SetDisplayOffset(1, ((y / h) - 0.5) * -8.0);
				return {x: undefined, y: y };
			}
		});

		elem.find("select.voltdiv.ch1").change( function(e) { me._SetVoltDivIdx(0, $(this).val()); });
		elem.find("select.voltdiv.ch2").change( function(e) { me._SetVoltDivIdx(1, $(this).val()); });
		elem.find("select.timediv").change( function(e) { me._SetTimeDivIdx($(this).val()); });

		for (var i in me._voltagesDisplay) {
			elem.find(".voltdiv.ch1").append('<option value="'+ i +'"' + (i == me._voltIdx[0] ? 'selected="selected"' : '') +' >' + me._voltagesDisplay[i] + '</option>');
			elem.find(".voltdiv.ch2").append('<option value="'+ i +'"' + (i == me._voltIdx[1] ? 'selected="selected"' : '') +' >' + me._voltagesDisplay[i] + '</option>');
		}
		for (var i in me._timedivsDisplay) {
			elem.find(".timediv").append('<option value="'+ i +'"' + (i == me._timeIdx ? 'selected="selected"' : '') +' >' + me._timedivsDisplay[i] + '</option>');
		}

		me._SetupGraphInteractions();
	});
};

extend(visir.NationalInstrumentOscilloscope, visir.Oscilloscope);

visir.NationalInstrumentOscilloscope.prototype._DrawGrid = function($elem)
{
	var context = $elem[0].getContext('2d');

	//context.strokeStyle = "#004000";
	context.strokeStyle = "#999999";
	context.lineWidth		= 0.5;
	context.beginPath();

	var len = 3.5;
	var w = $elem.width() - 1;
	var h = $elem.height() - 1;
	var xspacing = w / 10;
	var yspacing = h / 8;
	var i, x, y;

	for(i=0;i<=10;i++) {
		x = xspacing * i;
		x = Math.round(x);
		x += 0.5;
		context.moveTo(x, 0);
		context.lineTo(x, h);
	}

	for(i=0;i<=8;i++) {
		y = yspacing * i;
		y = Math.round(y);
		y += 0.5;
		context.moveTo(0, y);
		context.lineTo(w, y);
	}

	context.stroke();
};

visir.NationalInstrumentOscilloscope.prototype._DrawPlot = function($elem)
{
	var context = $elem[0].getContext('2d');
	context.strokeStyle = "#00ff00";
	context.lineWidth		= 1.2;

	var w = this._plotWidth; //$elem.width();
	var h = this._plotHeight; //$elem.height();
	context.clearRect(0,0, w, h);

	var me = this;
	// local draw function
	function DrawChannel(chnr, color) {
		if (!me._channels[chnr].visible) { return; }
		context.beginPath();
		context.strokeStyle = color;
		var ch = me._channels[chnr];
		var graph = ch.graph;
		var len = graph.length;
		for(var i=0;i<len;i++) {
			var x = i*w / len;
			var y = -((graph[i] / ch.range) + ch.display_offset) * (h / 8.0) + h/2;
			y+=0.5;
			if (i===0) {
				context.moveTo(x,y);
			} else {
				context.lineTo(x,y);
			}
		}
		context.stroke();
	}

	DrawChannel(1, "#9095f9");
	DrawChannel(0, "#FFFFFF");
};

visir.NationalInstrumentOscilloscope.prototype.ReadResponse = function(response) {
	visir.NationalInstrumentOscilloscope.parent.ReadResponse.apply(this, arguments);
	this._DrawPlot(this._$elem.find(".plot"));

	// check if we should continue measuring
	if (this._isMeasuringContinuous && this._options.CheckToContinueCalling()) {
		this._options.MeasureCalling();
	} else {
		this._isMeasuringContinuous = false;
	}
};

visir.NationalInstrumentOscilloscope.prototype._SetDisplayOffset = function(ch, offset) {
	this._channels[ch].display_offset = offset;
	this._channels[ch].offset = this._voltages[this._voltIdx[ch]] * -this._channels[ch].display_offset;
	//trace("_SetDisplayOffset: " + offset + " " + this._channels[ch].offset);

	this._DrawPlot(this._$elem.find(".plot"));
	this._UpdateTrigger();
};

visir.NationalInstrumentOscilloscope.prototype._UpdateTrigger = function() {
	var $trigger = this._$elem.find(".offsetbox.trigger");
	var h = $trigger.parent().height();

	var trigch = this._channels[this._trigger.source - 1];
	var level = this._trigger.level;

	var markerPos = (((-level + trigch.offset) / trigch.range) ) * (h / 8.0) + (h / 2.0);
	markerPos = Math.round(markerPos);
	$trigger.css("top", markerPos + "px");
};

visir.NationalInstrumentOscilloscope.prototype._SetTriggerLevel = function(level) {
	this._trigger.level = level;
}

visir.NationalInstrumentOscilloscope.prototype._SetVoltDivIdx = function(ch, idx) {
	if (idx < 0) idx = 0;
	if (idx >= this._voltages.length) idx = this._voltages.length - 1;
	trace("_SetVoltDivIdx: " + ch + " " + idx);

	this._voltIdx[ch] = idx;
	this._channels[ch].range = this._voltages[idx];
	this._channels[ch].offset = this._voltages[idx] * -this._channels[ch].display_offset;
	this._UpdateTrigger();
	this._DrawPlot(this._$elem.find(".plot"));
	this._$elem.find("select.voltdiv.ch" + (ch+1)).val(idx);
}

visir.NationalInstrumentOscilloscope.prototype._SetTimeDivIdx = function(idx) {
	if (idx < 0) idx = 0;
	if (idx >= this._timedivs.length) idx = this._timedivs.length - 1;

	trace("_SetTimeDivIdx: " + idx);

	this._timeIdx = idx;
	this._sampleRate = 1.0 / this._timedivs[this._timeIdx];
	this._DrawPlot(this._$elem.find(".plot"));
	this._$elem.find("select.timediv").val(idx);
}

visir.NationalInstrumentOscilloscope.prototype._SetupGraphInteractions = function()
{
	var me = this;
	var timer = null;

	/*
		make mouse wheel scrolling zoom the current channel
		if horizontal scroll is available, it will change the time div
	*/
	this._$elem.find(".clickarea").on("mousewheel", function(e) {
		trace("mousewheel");
		e.preventDefault();
		var deltaY = e.originalEvent.wheelDeltaY; // non portable?
		var deltaX = e.originalEvent.wheelDeltaX; // non portable?

		if (Math.abs(deltaY) > Math.abs(deltaX)) deltaX = 0;
		else deltaY = 0;

		// don't allow more than one scroll event per half-second
		if (timer) return false;
		timer = setTimeout(function() { clearInterval(timer); timer = null; }, 500);

		if (deltaY > 0) {
			me._SetVoltDivIdx(0, me._voltIdx[0] + 1);
		} else if (deltaY < 0) {
			me._SetVoltDivIdx(0, me._voltIdx[0] - 1);
		}

		if (deltaX > 0) {
			me._SetTimeDivIdx(me._timeIdx - 1);
		} else if (deltaX < 0) {
			me._SetTimeDivIdx(me._timeIdx + 1);
		}

	});

	/*
		Make two finger interaction on the graph work as pinch zoom in and out.
	*/
	var me = this;
	var $touch = this._$elem.find(".clickarea");
	$touch.on("gesturestart", function(e) {
		e.preventDefault();

		var deg = 0;

		$touch.on("touchmove.rem", function(e) {
			if (e.originalEvent.touches && e.originalEvent.touches < 2) return;
			var t1 = e.originalEvent.touches[0];
			var t2 = e.originalEvent.touches[1];
			if (t2.pageY < t1.pageY) {
				var tmp = t1;
				t1 = t2;
				t2 = tmp;
			}
			var dx = t2.pageX - t1.pageX;
			var dy = t2.pageY - t1.pageY;
			deg = Math.atan2(dy, dx) * 180 / Math.PI;
		});

		$touch.on("gestureend.rem", function(e) {
			$touch.off(".rem");

			//if (timer) return false;
			//timer = setTimeout(function() { clearInterval(timer); timer = null; }, 500);

			var scale = e.originalEvent.scale;
			var rot = e.originalEvent.rotation;
			trace(new Date().getTime() + " scale: " + scale + " " + rot + " " + deg);

			var cutoff= 35;
			if ((deg > 180 - cutoff) || (deg < cutoff)) {
				trace("horizontal");
				if (scale > 1.4) me._SetTimeDivIdx(me._timeIdx + 1);
				else if (scale < 0.6) me._SetTimeDivIdx(me._timeIdx - 1);
			}
			else {
				trace("vertical");
				if (scale > 1.4) me._SetVoltDivIdx(0, me._voltIdx[0] + 1);
				else if (scale < 0.6) me._SetVoltDivIdx(0, me._voltIdx[0] - 1);
			}
		});

		//var scale = e.originalEvent.scale;
		//trace("scale: " + scale);

		/*if (timer) return false;
		timer = setTimeout(function() { clearInterval(timer); timer = null; }, 500);

		//var scale = e.originalEvent.scale;
		//trace("scale: " + scale);

		if (scale > 1.2) {
			me._SetVoltDivIdx(0, me._voltIdx[0] + 1);
		} else if (scale < 0.8) {
			me._SetVoltDivIdx(0, me._voltIdx[0] - 1);
		}*/
	});
}