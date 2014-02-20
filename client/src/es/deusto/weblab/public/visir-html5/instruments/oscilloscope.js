"use strict";

var visir = visir || {};

visir.Oscilloscope = function(id)
{
	this._id = id;

	this._autoScale = 0;
	this._sampleRate = 500; // ?
	this._horzRefPos = 50;
	this._recordLength = 500; // number of samples to aquire

	function NewGraph(l)
	{
		var out = new Array(l);
		for(var i=0; i<l; i++) { out[i] = 0.0; }
		return out;
	}

	var channel1 = { enabled: 1, coupling: "dc", range: 1, offset: 0, attenuation: 1.0, graph: NewGraph(500) };
	var channel2 = { enabled: 1, coupling: "dc", range: 1, offset: 0, attenuation: 1.0, graph: NewGraph(500) };
	this._channels = [ channel1, channel2 ];

	this._trigger = {
		source: 1 //"channel 1"
		, slope: "positive"
		, coupling: "dc"
		, level: 0.0
		, mode: "autolevel"
		, timeout: 1.0
		, delay: 0.0
	}

	/*var m1 = { channel: 1, selection: "none", result: "" };
	var m2 = { channel: 1, selection: "none", result: "" };
	var m3 = { channel: 1, selection: "none", result: "" };*/
	this._measurements = [];
}

// XXX: the extra parameter is a horrible hack..
visir.Oscilloscope.prototype.AddMeasurement = function(ch, selection, extra)
{
	var rv = -1;
	for(var i=0;i<this._measurements.length; i++) {
		if (this._measurements[i].channel == ch && this._measurements[i].selection == selection) {
			this._measurements.splice(i, 1);
			rv = i;
			break;
		}
	}

	while(this._measurements.length > 2) this._measurements.shift();
	this._measurements.push( { channel: ch, selection: selection, extra: extra, result: "" } );
	return rv;
}

visir.Oscilloscope.prototype.WriteRequest = function()
{
	var $xml = $('<oscilloscope><horizontal/><channels/><trigger/><measurements/></oscilloscope>');
	$xml.attr("id", this._id);

	AddXMLValue($xml, "osc_autoscale", this._autoScale);

	// horizontal
	var $horz = $xml.find("horizontal");
	AddXMLValue($horz, "horz_samplerate", this._sampleRate);
	AddXMLValue($horz, "horz_refpos", this._horzRefPos);
	AddXMLValue($horz, "horz_recordlength", this._recordLength);

	// assume 2 channels
	for(var i=0; i<2; i++) {
		var ch = this._channels[i];
		var $channel = $('<channel/>');
		$channel.attr("number", i+1);
		AddXMLValue($channel, "chan_enabled", ch.enabled);
		AddXMLValue($channel, "chan_coupling", ch.coupling);
		AddXMLValue($channel, "chan_range", ch.range);
		AddXMLValue($channel, "chan_offset", ch.offset);
		AddXMLValue($channel, "chan_attenuation", ch.attenuation);
		$xml.find("channels").append($channel);
	}

	var $trigger = $xml.find("trigger");
	var trig = this._trigger;
	AddXMLValue($trigger, "trig_source", "channel " + trig.source);
	AddXMLValue($trigger, "trig_slope", trig.slope);
	AddXMLValue($trigger, "trig_coupling", trig.coupling);
	AddXMLValue($trigger, "trig_level", trig.level);
	AddXMLValue($trigger, "trig_mode", trig.mode);
	AddXMLValue($trigger, "trig_timeout", trig.timeout);
	AddXMLValue($trigger, "trig_delay", trig.delay);

	for(var i=0; i<3; i++) {
		var channel = 1;
		var selection = "none";
		if (i < this._measurements.length) {
			var meas = this._measurements[i];
			channel = meas.channel;
			selection = meas.selection;
		}

		var $measure = $('<measurement/>');
		$measure.attr("number", i+1);
		AddXMLValue($measure, "meas_channel", "channel " + channel);
		AddXMLValue($measure, "meas_selection", selection);
		$xml.find("measurements").append($measure);
	}

	return $("<root />").append($xml).html();
}

visir.Oscilloscope.prototype.ReadResponse = function(response) {
	var me = this;
	var $xml = $(response);
	var $oscilloscope = $xml.find("oscilloscope"); // add id match later, when server supports it
	if ($oscilloscope.length == 0) return;

	$oscilloscope.find("channel").each(function() {
		var $channel = $(this);
		var chnr = $channel.attr("number");
		var $samples = $channel.find("chan_samples");
		if ($samples.attr("encoding") != "base64") throw "unknown encoding";
		var gain = parseFloat($channel.find("chan_gain").attr("value"));
		var offset = parseFloat($channel.find("chan_offset").attr("value"));
		var base64text = $samples.text();
		var a = base64_decode(base64text);
		var graph = [];
		for(var i in a) {
			if (a[i] > 127) a[i] = a[i] - 256;
			graph[i] = a[i] * gain + offset;
		}
		me._channels[chnr - 1].graph = graph;
	});

	$oscilloscope.find("measurement").each(function() {
		var $measurement = $(this);
		var measnr = parseInt($measurement.attr("number"), 10);
		var channel = $measurement.find("meas_channel").attr("value");
		var selection = $measurement.find("meas_selection").attr("value");
		var result = parseFloat($measurement.find("meas_result").attr("value"));
		if (me._measurements.length >= measnr) me._measurements[measnr - 1].result = result;
	});
}
