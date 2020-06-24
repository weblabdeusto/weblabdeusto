"use strict";

var visir = visir || {};

visir.TripleDC = function(id, elem)
{
	visir.TripleDC.parent.constructor.apply(this, arguments)

	this._elem = elem;
	this._id = id;

	this._Redraw([0, 0, 0]);
};

extend(visir.TripleDC, visir.DCPower)

visir.TripleDC.prototype._Redraw = function (initialValue) 
{
	var me = this;
	var dcPower25 = (visir.Config) ? visir.Config.Get("dcPower25") : true;
	var dcPowerM25 = (visir.Config) ? visir.Config.Get("dcPowerM25") : true;
	var dcPower6 = (visir.Config) ? visir.Config.Get("dcPower6") : true;

	this.dcPower6 = dcPower6;
	this.dcPower25 = dcPower25;
	this.dcPowerM25 = dcPowerM25;

	this._elem.empty();

	if (dcPower6) {
		this._activeChannel = "6V+";
	} else if (dcPower25) {
		this._activeChannel = "25V+";
	} else if (dcPowerM25) {
		this._activeChannel = "25V-";
	} else {
		// No dcPower?
		return;
	}

	// all the values are represented times 1000 to avoid floating point trouble
	// XXX: need to change this later, both voltage and current has an active digit
	this._values = {
		"6V+": { voltage: 0, current: 5000, digit: 2, min: 0, max: 6000},
		"25V+": { voltage: 0, current: 5000, digit: 2, min: 0, max: 25000 },
		"25V-": { voltage: 0, current: 5000, digit: 2, min: -25000, max: 0 }
	 }

	var imgbase = "instruments/tripledc/images";
	if (visir.BaseLocation) imgbase = visir.BaseLocation + imgbase;

	var tpl = '<div class="tripledc">\
	<img src="%img%/3dc.png" width="720" height="449" draggable="false" />\
	<div class="bigtext voltage"><span class="green">0</span>.000V</div>\
	<div class="bigtext current">0.500A</div>\
	<div class="channelselect">\n'

	if (dcPower6) {
		tpl += '<div class="smalltext p6v">+6V</div>';
	}

	if (dcPower25) {
		if (this._activeChannel == "25V+") {
			tpl += '<div class="smalltext p25v">+25V</div>';
		} else {
			tpl += '<div class="smalltext p25v hide">+25V</div>';
		}
	}

	if (dcPowerM25) {
		if (this._activeChannel == "25V-") {
			tpl += '<div class="smalltext m25v">-25V</div>';
		} else {
			tpl += '<div class="smalltext m25v hide">-25V</div>';
		}
	}
	tpl += '</div>\n';
	if (dcPower6) {
		tpl += '<div class="button button_p6v"><img class="up active" src="%img%/6v_up.png" alt="+6v button" /><img class="down" src="%img%/6v_down.png" alt="+6v button" /></div>\n';
	}
	if (dcPower25) {
		tpl += '<div class="button button_p25v"><img class="up active" src="%img%/25plusv_up.png" alt="+25v button" /><img class="down" src="%img%/25plusv_down.png" alt="+25v button" /></div>\n';
	}
	if (dcPowerM25) {
		tpl += '<div class="button button_m25v"><img class="up active" src="%img%/25minusv_up.png" alt="-25v button" /><img class="down" src="%img%/25minusv_down.png" alt="-25v button" /></div>\n';
	}
	tpl += '<div class="button button_left"><img class="up active" src="%img%/arrowleft_up.png" alt="left button" /><img class="down" src="%img%/arrowleft_down.png" alt="left button" /></div>\
	<div class="button button_right"><img class="up active" src="%img%/arrowright_up.png" alt="right button" /><img class="down" src="%img%/arrowright_down.png" alt="right button" /></div>\
	<div class="knob">\
		<div class="top">\
			<img src="%img%/3dc_wheel.png" alt="handle" />\
		</div>\
	</div>\
	<div class="manual_link"><a href="http://cp.literature.agilent.com/litweb/pdf/E3631-90002.pdf" target="_blank">%downloadManual%</a></div>\
	</div>';

	tpl = tpl.replace(/%img%/g, imgbase);
	tpl = tpl.replace(/%downloadManual%/g, visir.Lang.GetMessage("down_man"));

	this._elem.append(tpl);

	if (dcPower6) {
		this._SetInitialValue("6V+", Number(initialValue[0]), 2);
	}
	if (dcPower25) {
		this._SetInitialValue("25V+", Number(initialValue[1]), 2);
	}
	if (dcPowerM25) {
		this._SetInitialValue("25V-", Number(initialValue[2]), 2);
	}
	if (dcPower6) {
		this._SetActiveChannel("6V+");
		this._activeChannel = "6V+";
	} else if (dcPower25) {
		this._SetActiveChannel("25V+");
		this._activeChannel = "25V+";
	} else if (dcPowerM25) {
		this._SetActiveChannel("25V-");
		this._activeChannel = "25V-";
	}

	var $doc = $(document);

	var prev = 0;

	function handleTurn(elem, deg) {
		var diff = deg - prev;
		// fixup the wrapping
		if (diff > 180) diff = -360 + diff;
		else if (diff < -180) diff = 360 + diff;

		if (Math.abs(diff) > 360/10) {
			prev = deg;
			//trace("diff: " + diff);
			if (diff < 0) me._DecDigit();
			else if (diff > 0) me._IncDigit();
		}

		return deg;
	}

	if(!visir.Config.Get("readOnly"))
	{
		this._elem.find(".knob").turnable({offset: 90, turn: handleTurn });

		// make all buttons updownButtons
		this._elem.find(".button").updownButton();

		this._elem.find("div.button_p6v").click( function() {
			me._SetActiveChannel("6V+");
		});
		this._elem.find("div.button_p25v").click( function() {
			me._SetActiveChannel("25V+");
		});
		this._elem.find("div.button_m25v").click( function() {
			me._SetActiveChannel("25V-");
		});
		this._elem.find("div.button_left").click( function() {
				var aCh = me._GetActiveChannel();
				trace("digit: " + (aCh.digit + 1));
				me._SetActiveValue(aCh.voltage, aCh.digit + 1);
		});
		this._elem.find("div.button_right").click( function() {
				var aCh = me._GetActiveChannel();
				trace("digit: " + (aCh.digit -1));
				me._SetActiveValue(aCh.voltage, aCh.digit - 1);
		});
	}

	// XXX: need to fix this when making it possible to change current limits
	var blink = this._elem.find(".tripledc .voltage");
	setInterval(function() {
		blink.toggleClass("on");
	},500);

	me._UpdateDisplay();
};

visir.TripleDC.prototype._UpdateDisplay = function(showMeasured) {
	showMeasured = showMeasured || false;
	var aCh = this._GetActiveChannel();
	var digitoffset = 0;
	if (aCh.voltage >= 10000) {
		digitoffset = 1;
	}

	var value = 0;
	if (showMeasured) {
		var responseData = this._channels[this._activeChannel];
		if (!responseData.enabled) return;
		value = responseData.measured_voltage;
		if (value == 0.0) return;
	} else {
		value = (aCh.voltage / 1000);
	}

	//var value = (showMeasured) ? this._channels[this._activeChannel].measured_voltage : (aCh.voltage / 1000);
	trace("value: " + value);

	//var fixed = (aCh.voltage >= 10000) ? 2 : 3;
	//var num = (aCh.voltage / 1000).toFixed(3 - digitoffset);
	var num = value.toFixed(3 - digitoffset);
	this._elem.find(".voltage").html(visir.LightNum(num, aCh.digit - digitoffset) + "V" );
}

visir.TripleDC.prototype._GetActiveChannel = function() {
	return this._values[this._activeChannel];
}

visir.TripleDC.prototype._SetActiveChannel = function(ch) {
	trace("activechannel: " + ch);
	this._activeChannel = ch;

	this._elem.find(".channelselect > div").addClass("hide");
	var show = "";
	switch(ch) {
		case "6V+": show = "p6v"; break;
		case "25V+": show = "p25v"; break;
		case "25V-": show = "m25v"; break;
		default: show = "p6v";
	}
	this._elem.find(".channelselect > div." + show).removeClass("hide");
	this._UpdateDisplay();
}

visir.TripleDC.prototype._SetActiveValue = function(val, digit) {
	var aCh = this._GetActiveChannel();
	if ((val < aCh.min) || (val > aCh.max)) return;
	if (digit > 4 || digit < 0) return;
	//trace("setactivevalue: " + val + " " + digit + " " + Math.pow(10, digit));
	if (val > 1000 && val < Math.pow(10, digit)) return;
	if (val < 10000 && digit == 4) return;
	aCh.voltage = val;
	aCh.digit = digit;
	this.GetChannel(this._activeChannel).voltage = (val / 1000);
	this._UpdateDisplay();
}

visir.TripleDC.prototype._DecDigit = function() {
	var aCh = this._GetActiveChannel();
	this._SetActiveValue(aCh.voltage - Math.pow(10, aCh.digit), aCh.digit);
}

visir.TripleDC.prototype._IncDigit = function() {
	var aCh = this._GetActiveChannel();
	this._SetActiveValue(aCh.voltage + Math.pow(10, aCh.digit), aCh.digit);
}

visir.TripleDC.prototype.ReadResponse = function(response) {
	var me = this;
	visir.TripleDC.parent.ReadResponse.apply(this, arguments);

	this._UpdateDisplay(true);
}

visir.TripleDC.prototype._ReadCurrentValues = function() {
	/* Only used if unrFormat = true */
	var volts = "";
	volts = this._channels["6V+"].voltage * 1000 + ":" + this._channels["25V+"].voltage  * 1000 + ":" + this._channels["25V-"].voltage  * 1000;
	return volts;
}

visir.TripleDC.prototype._SetInitialValue = function(ch, val, digit) {
	this._activeChannel = ch;
	this._SetActiveValue(val,digit);
}

visir.TripleDC.prototype.ReadSave = function($xml)
{
	var initialValue = [0, 0, 0];

	// Only for backwards compatibility
	var $instrumentsvalues = $xml.find("instrumentsvalues");
	if ($instrumentsvalues.length == 1) {
		var htmlinstrumentsvalues = $instrumentsvalues.attr("htmlinstrumentsvalues");
		if (htmlinstrumentsvalues) {
			$.each(htmlinstrumentsvalues.split("|"), function (pos, instrumentData) {
				var instrumentName = instrumentData.split("#")[0];
				if (instrumentName == "TripleDC") {
					var numbers = instrumentData.split("#")[1].split(":");
					initialValue = [ parseInt(numbers[0]), parseInt(numbers[1]), parseInt(numbers[2]) ];
				}
			});
		}
	}

	if (this.dcPower6) {
		var $dcPower6voltage = $xml.find("dc_output[channel='6V+']");
		if ($dcPower6voltage.length == 1) {
			initialValue[0] = Number($dcPower6voltage.attr("value"));
		}
	}

	if (this.dcPower25) {
		var $dcPower25voltage = $xml.find("dc_output[channel='25V+']");
		if ($dcPower25voltage.length == 1) {
			initialValue[1] = Number($dcPower25voltage.attr("value"));
		}
	}

	if (this.dcPowerM25) {
		var $dcPowerM25voltage = $xml.find("dc_output[channel='25V-']");
		if ($dcPowerM25voltage.length == 1) {
			initialValue[2] = Number($dcPowerM25voltage.attr("value"));
		}
	}

	this._Redraw(initialValue);
}

visir.TripleDC.prototype.WriteSave = function()
{
	var $xml = $("<dcpower></dcpower>");
	if (this.dcPower6) {
		var channel = $("<dc_output channel=\"6V+\" value=\"" + (this._channels["6V+"].voltage * 1000) + "\"/>");
		$xml.append(channel);
	}
	if (this.dcPower25) {
		var channel = $("<dc_output channel=\"25V+\" value=\"" + (this._channels["25V+"].voltage * 1000) + "\"/>");
		$xml.append(channel);
	}
	if (this.dcPowerM25) {
		var channel = $("<dc_output channel=\"25V-\" value=\"" + (this._channels["25V-"].voltage * 1000) + "\"/>");
		$xml.append(channel);
	}
	return $xml;
};
