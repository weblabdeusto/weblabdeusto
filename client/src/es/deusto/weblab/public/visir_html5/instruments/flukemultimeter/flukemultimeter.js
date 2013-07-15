"use strict";
var visir = visir || {};

visir.FlukeMultimeter = function(id, elem)
{
	//"off", "ac volts", "dc volts", "off", "resistance", "off", "ac current", "dc current");
	//var rotFuncMap = { 345: "off", 15: "ac volts", 45: "dc volts", 75: "off", 105: "resistance", 135: "off", 165: "ac current", 195: "dc current"};
	
	var dmm = this;
	this._elem = elem;
	this._result = "";
	
	visir.FlukeMultimeter.parent.constructor.apply(this, arguments)
	
	var imgbase = "instruments/flukemultimeter/";
	if (visir.BaseLocation) imgbase = visir.BaseLocation + imgbase;
	
	var tpl = '<div class="flukedmm">\
	<img src="' + imgbase + 'fluke23.png" width="300" height="460" />\
	<div class="dmm_value" id="value">12.3</div>\
	<div class="rot">\
		<div class="top vred">\
			<img src="' + imgbase + 'fluke23_vred.png" alt="handle" />\
		</div>\
	</div>\
	</div>';
		
	elem.append(tpl);
	
	var top = elem.find(".top");
	setRotation(top, 345);
	
	var handle = elem.find(".rot");
	
	function handleTurn(elem, deg)
	{
		deg = ( deg - deg % 30 )  + 15;

		if (deg <= 105 || deg >= 255)
		{
			setRotation(top, deg);

			var rotFuncMap = { 255: "off", 285: "ac volts", 315: "dc volts", 345: "off", 15: "resistance", 45: "off", 75: "ac current", 105: "dc current"};
			var mode = rotFuncMap[deg];
			dmm.SetMode(mode);
			if (mode == "off") dmm._result = "";
			else if (mode == "resistance") dmm._result = "OL";
			else dmm._result = 0.0;
			dmm.UpdateDisplay();
			return deg;
		}
		return undefined; // don't set a new rotation
	}
	
	handle.turnable({ offset: 90, turn: handleTurn })
	
	dmm.UpdateDisplay();
}

extend(visir.FlukeMultimeter, visir.Multimeter)

visir.FlukeMultimeter.prototype.Test = function() {
	
}

visir.FlukeMultimeter.prototype.UpdateDisplay = function() {
	var $value = this._elem.find(".dmm_value");
	if (this.GetMode() == "off") {
		$value.text("");
	} else {
		var out = this.GetResult();
		
		trace("DMM RESULT: " + out);
		
		if (typeof out == "number") {
			var unit = this._GetUnit(out);
			out = out / Math.pow(10, unit.pow);

			out = out.toPrecision(4);
			$value.text(out + unit.unit);
		}
		else {
			$value.text(out);
		}
	}
}

visir.FlukeMultimeter.prototype.ReadResponse = function(response) {
	visir.FlukeMultimeter.parent.ReadResponse.apply(this, arguments)
	this.UpdateDisplay();
}

visir.FlukeMultimeter.prototype._GetUnit = function(val)
{
	var units = [
		["G", 6 ]
		, ["M", 6 ]
		, ["k", 3 ]
		, ["", 0]
		, ["m", -3]
		, ["u", -6]
		, ["n", -9]
		];
	val = Math.abs(val);
	var unit = "";
	var div = 0;
	if (val == 0) return { unit: unit, pow: div };
	
	for (var key in units) {
		var unit = units[key];
		if (val >= Math.pow(10, unit[1])) {
			return {unit: unit[0], pow: unit[1] };
		}
	}
	
	var last = units[units.length - 1];
	return {unit: last[0], pow: last[1] };
}
