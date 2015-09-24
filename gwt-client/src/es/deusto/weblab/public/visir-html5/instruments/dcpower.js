"use strict";

var visir = visir || {};

visir.DCPower = function(id)
{
	this._id = id;
	this._channels = {
		"6V+": { voltage: 0.0, current: 0.5, measured_voltage: 0, measured_current: 0, limited: 0, enabled: 0 },
		"25V+": { voltage: 0.0, current: 0.5, measured_voltage: 0, measured_current: 0, limited: 0, enabled: 0 },
		"25V-": { voltage: 0.0, current: 0.5, measured_voltage: 0, measured_current: 0, limited: 0, enabled: 0 }
	 }
}

// XXX: Should probably fix a nicer interface for changing the settings
visir.DCPower.prototype.GetChannel = function(ch)
{
	return this._channels[ch];
}
	
visir.DCPower.prototype.WriteRequest = function()
{
	var $xml = $("<dcpower><dc_outputs/></dcpower>");
	$xml.attr("id", this._id);
	var $outputs = $xml.find("dc_outputs");
	for(var key in this._channels)
	{
		var ch = this._channels[key];
		var $channel = $("<dc_output/>");
		$channel.attr("channel", key);
		AddXMLValue($channel, "dc_voltage", ch.voltage);
		AddXMLValue($channel, "dc_current", ch.current);
		$outputs.append($channel);
	}	
	
	// XXX: trick to get a valid root doc
	return $("<root />").append($xml).html();
},

visir.DCPower.prototype.ReadResponse = function(response) {
	var me = this;
	var $xml = $(response);
	var $dcpower = $xml.find("dcpower"); // add id match later, when server supports it
	if ($dcpower.length == 0) return;
	//trace("xml: " + $dcpower.html());
	
	$dcpower.find("dc_output").each(function() {
		var $channel = $(this);
		var chname = $channel.attr("channel");
		var actual_voltage = parseFloat($channel.find("dc_voltage_actual").attr("value"));
		var actual_current = parseFloat($channel.find("dc_current_actual").attr("value"));
		var enabled = parseInt($channel.find("dc_output_enabled").attr("value"));
		var limited = parseInt($channel.find("dc_output_limited").attr("value"));
		if (me._channels[chname]) {
			me._channels[chname].measured_voltage = actual_voltage;
			me._channels[chname].measured_current = actual_current;
			me._channels[chname].limited = limited;
			me._channels[chname].enabled = enabled;
		}
	});
}
