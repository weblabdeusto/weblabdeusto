"use strict";

var visir = visir || {};

visir.Multimeter = function(id)
{
	this._id = id;
	this._mode = "off";
	this._resolution = "3.5";
	this._range = 10;
	this._autozero = 1;
	this._result = 0.0;
}

visir.Multimeter.prototype.SetMode = function(mode) { this._mode = mode; },
visir.Multimeter.prototype.GetMode = function() { return this._mode; },

visir.Multimeter.prototype.GetResult = function() { return this._result },
	
visir.Multimeter.prototype.WriteRequest = function()
{
	if (this._mode == "off") return ""; //'<multimeter id="'+ this._id + '" />';
	
	var $xml = $('<multimeter />');
	$xml.attr("id", this._id);
	
	var values = {
		dmm_function: this._mode
		, dmm_resolution: this._resolution
		, dmm_range: this._range
		, dmm_autozero: this._autozero
	};
	
	for (var key in values) {
		AddXMLValue($xml, key, values[key]);
	}
	
	// XXX: trick to get a valid root doc
	return $("<root />").append($xml).html();
},

visir.Multimeter.prototype.ReadResponse = function(response) {
	var $xml = $(response);
	var $multimeter = $xml.find("multimeter[id=" + this._id + "]");
	if ($multimeter.length > 0) {
		var result = $multimeter.find("dmm_result").attr("value");
		if (!isNaN(result))	{
			this._result = parseFloat(result);
		} else {
			this._result = NaN;
		}
	}	
}
