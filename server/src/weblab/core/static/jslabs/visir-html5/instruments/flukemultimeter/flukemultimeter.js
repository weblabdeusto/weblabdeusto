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
	<img src="' + imgbase + 'fluke23.png" width="300" height="460" draggable="false" />\
	<div class="display">\
		<div class="dmm_value" id="value">12.3</div>\
		<div class="mode AC">VAC</div>\
		<div class="mode DC">VDC</div>\
		<div class="mode Ohm">&#8486;</div>\
		<div class="unit"></div>\
	</div>\
	<div class="rot">\
		<div class="top vred">\
			<img src="' + imgbase + 'fluke23_vred.png" alt="handle" />\
		</div>\
	</div>\
	<div class="manual_link"><a href="http://assets.fluke.com/manuals/23______omeng0000.pdf" target="_blank">%downloadManual%</a></div>\
	</div>';

	tpl = tpl.replace(/%downloadManual%/g, visir.Lang.GetMessage("down_man"));
	elem.append(tpl);

	var top = elem.find(".top");
	setRotation(top, 345);

	var handle = elem.find(".rot");

	function handleTurn(elem, deg)
	{
		if (!visir.Config.Get("readOnly"))
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
	if (this.GetMode() == "off") {
		this._elem.find(".display").toggle(false);		
		return;
	}
	
	this._elem.find(".display").toggle(true);
	this._elem.find(".display .mode").toggle(false);
	
	var result = this.GetResult();
	var unit = "";
	var out = 0.0;
	
	if (isNaN(result)) {
		out = "OL"; unit = "M";
	}	else {
		var unitinfo = this._GetUnit(result);
		out = result / Math.pow(10, unitinfo.pow);
		out = out.toPrecision(4);
		unit = unitinfo.unit;
	}
		
	this._elem.find(".dmm_value").text(out);
	
	switch(this.GetMode())
	{
		case "ac volts":
			this._elem.find(".display .mode.AC").toggle(true).text( unit + "VAC");
			break;
		case "dc volts":
			this._elem.find(".display .mode.DC").toggle(true).text( unit +"VDC");
			break;
		case "resistance":
			this._elem.find(".display .mode.Ohm").toggle(true).html( unit + '&#8486;');
			break;
		case "ac current":
			this._elem.find(".display .mode.AC").toggle(true).text( unit + "AC");
			break;
		case "dc current":
			this._elem.find(".display .mode.DC").toggle(true).text( unit + "DC");
			break;
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

visir.FlukeMultimeter.prototype.ReadSave = function($xml)
{
	var $multimeter = $xml.find("multimeter[id='" + this._id + "']");
	if ($multimeter.length == 1) {
		var mode = $multimeter.attr("mode");
		this.SetMode(mode);

		switch (mode) {
			case 'ac volts':
			  setRotation(this._elem.find(".top"), 15);
			  break;
			case 'dc volts':
			  setRotation(this._elem.find(".top"), 45);
			  break;
			case 'resistance':
			  setRotation(this._elem.find(".top"), 105);
			  break;
			case 'ac current':
			  setRotation(this._elem.find(".top"), 165);
			  break;
			case 'dc current':
			  setRotation(this._elem.find(".top"), 195);
			  break;
			default:
			  setRotation(this._elem.find(".top"), 345);
			  break;
		}
		this.UpdateDisplay();
	}
}

visir.FlukeMultimeter.prototype.WriteSave = function()
{
	return $("<multimeter id='" + this._id + "'></multimeter>").attr("mode", this.GetMode());
};
