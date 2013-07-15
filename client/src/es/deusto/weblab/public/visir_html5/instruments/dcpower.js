"use strict";

var visir = visir || {};

visir.DCPower = function(id)
{
	this._id = id;
	this._channels = {
		"6V+": { voltage: 0.0, current: 0.5 },
		"25V+": { voltage: 0.0, current: 0.5 },
		"25V-": { voltage: 0.0, current: 0.5}
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
}
