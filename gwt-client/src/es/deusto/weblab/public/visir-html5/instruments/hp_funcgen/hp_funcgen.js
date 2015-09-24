"use strict";

var visir = visir || {};

visir.HPFunctionGenerator = function(id, elem)
{
	visir.HPFunctionGenerator.parent.constructor.apply(this, arguments)

	var me = this;
	this._$elem = elem;
	this._currentValue = "freq";

	this.ENTERNUM = 1;
	this.NORMAL = 0;
	this._enterMode = this.NORMAL;
	this._enterNumStr = "";

	/* the multipliers are used to avoid storing the values in floating point
	which will cause problems when trying to display the values */
	this._values = {
		"freq": { value: 1000 * 100000000, multiplier: 100000000, digit: 8, numDigits: 8, unit: "Hz", max: 1*1000*1000*100000000, min: 10000},
		"ampl": { value: 1 * 10000, multiplier: 10000, digit: 4, numDigits: 4, unit: "Vpp", max: 10*10000, min: 500 },
		"offset": { value: 0, multiplier: 10000, digit: 4, numDigits: 4, unit: "VDC", max: 10*10000, min: -10*10000 }
	 }

	var imgbase = "instruments/hp_funcgen/images";
	if (visir.BaseLocation) imgbase = visir.BaseLocation + imgbase;

	var tpl =
	'<div class="hp_funcgen">\
	<img src="%img%/fgen.png" width="800" height="356" draggable="false" />\
	<div class="bigtext num_display">1.00<span class="green">0</span>0000</div>\
	<div class="bigtext num_unit">KHz</div>\
	<div class="funcselect">\
		<img class="sine active" src="%img%/sine.svg" alt="sine" />\
		<img class="square" src="%img%/square.svg" alt="square" />\
		<img class="triangle" src="%img%/tri.svg" alt="triangle" />\
		<img class="rampup" src="%img%/saw.svg" alt="sawtooth" />\
	</div>\
	<div class="button button_sine"><img class="up active" src="%img%/reflad_sin_up.png" alt="sine button" /><img class="down" src="%img%/reflad_sin_down.png" alt="sine button" /></div>\
	<div class="button button_square"><img class="up active" src="%img%/reflad_square_up.png" alt="square button" /><img class="down" src="%img%/reflad_square_down.png" alt="square button" /></div>\
	<div class="button button_triangle"><img class="up active" src="%img%/reflad_tri_up.png" alt="tri button" /><img class="down" src="%img%/reflad_tri_down.png" alt="tri button" /></div>\
	<div class="button button_rampup"><img class="up active" src="%img%/reflad_saw_up.png" alt="saw button" /><img class="down" src="%img%/reflad_saw_down.png" alt="saw button" /></div>\
	<div class="button button_noise"><img class="up active" src="%img%/reflad_noise_up.png" alt="noise button" /><img class="down" src="%img%/reflad_noise_down.png" alt="noise button" /></div>\
	<div class="button button_arb"><img class="up active" src="%img%/reflad_arb_up.png" alt="arb button" /><img class="down" src="%img%/reflad_arb_down.png" alt="arb button" /></div>\
	<div class="button button_enter"><img class="up active" src="%img%/enter_up.png" alt="enter button" /><img class="down" src="%img%/enter_down.png" alt="enter button" /></div>\
	<div class="button button_freq"><img class="up active" src="%img%/ren_freq_up.png" alt="freq button" /><img class="down" src="%img%/ren_freq_down.png" alt="freq button" /></div>\
	<div class="button button_ampl"><img class="up active" src="%img%/ren_ampl_up.png" alt="ampl button" /><img class="down" src="%img%/ren_ampl_down.png" alt="ampl button" /></div>\
	<div class="button button_offset"><img class="up active" src="%img%/ren_offset_up.png" alt="offset button" /><img class="down" src="%img%/ren_offset_down.png" alt="offset button" /></div>\
	<div class="button button_single"><img class="up active" src="%img%/ren_single_up.png" alt="single button" /><img class="down" src="%img%/ren_single_down.png" alt="single button" /></div>\
	<div class="button button_recall"><img class="up active" src="%img%/ren_recall_up.png" alt="recall button" /><img class="down" src="%img%/ren_recall_down.png" alt="recall button" /></div>\
	<div class="button button_enternumber"><img class="up active" src="%img%/ren_enternumber_up.png" alt="enternumber button" /><img class="down" src="%img%/ren_enternumber_down.png" alt="enternumber button" /></div>\
	<div class="button button_shift"><img class="up active" src="%img%/shift_up.png" alt="shift button" /><img class="down" src="%img%/shift_down.png" alt="shift button" /></div>\
	<div class="button button_up"><img class="up active" src="%img%/small_up_up.png" alt="up button" /><img class="down" src="%img%/small_up_down.png" alt="up button" /></div>\
	<div class="button button_down"><img class="up active" src="%img%/small_down_up.png" alt="down button" /><img class="down" src="%img%/small_down_down.png" alt="down button" /></div>\
	<div class="button button_right"><img class="up active" src="%img%/small_right_up.png" alt="right button" /><img class="down" src="%img%/small_right_down.png" alt="right button" /></div>\
	<div class="button button_left"><img class="up active" src="%img%/small_left_up.png" alt="left button" /><img class="down" src="%img%/small_left_down.png" alt="left button" /></div>\
	<div class="knob">\
		<div class="top">\
			<img src="%img%/wheel.png" alt="handle" />\
		</div>\
	</div>\
	<div class="manual_link"><a href="http://www.home.agilent.com/upload/cmc_upload/All/6C0633120A_USERSGUIDE_ENGLISH.pdf" target="_blank">Download Manual</a></div>\
	</div>';

	tpl = tpl.replace(/%img%/g, imgbase);
	//console.log(tpl);

	elem.append(tpl);

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

	function buttonPressGen(name) {
		return function() {
			me._ButtonPressed(name);
		}
	}

	if(!visir.Config.Get("readOnly"))
	{
		elem.find(".knob").turnable({offset: 90, turn: handleTurn });

		// make all buttons updownButtons
		elem.find(".button").updownButton();

		var buttons = [ "sine", "square", "triangle", "rampup", "noise",
			"arb", "enter", "freq", "ampl", "offset",
			"single", "recall", "enternumber", "shift", "up",
			"down", "right", "left"] ;

		for (var i in buttons) {
			elem.find("div.button_" + buttons[i]).click( buttonPressGen(buttons[i]) );
		}
	}

	var blink = elem.find(".hp_funcgen .num_display");
	setInterval(function() {
		blink.toggleClass("on");
	},500);

	me._UpdateDisplay();
}

extend(visir.HPFunctionGenerator, visir.FunctionGenerator)


function numDigits(val)
{
	val = Math.abs(val);
	var out = 1;
	var t = 10;
	while(val >= t) {
		t *= 10;
		out++;
	}
	return out;
}

/*
function CountNum(str)
{
	var cnt = 0;
	for(var i in str) {
		if (str[i] >= '0' && str[i] <= '9') cnt++;
	}
	return cnt;
}

function GetLightNumOffset(value, digits)
{
	var num = CountNum(value.toFixed(digits));
	return num - digits;
}*/

visir.HPFunctionGenerator.prototype._SetButtonMode = function(mode)
{
	this._enterMode = mode;
	this._enterNumStr = "";
}

visir.HPFunctionGenerator.prototype._AddNum = function(char)
{
	if (this._enterNumStr.length > this._values[this._currentValue].numDigits) return false;
	if ((char == '.') && (this._enterNumStr.indexOf(".") >= 0)) return false;
	this._enterNumStr += char;
}

visir.HPFunctionGenerator.prototype._RemoveNum = function()
{
	if (this._enterNumStr.length == 0) return false;
	this._enterNumStr = this._enterNumStr.slice(0, -1);
}

visir.HPFunctionGenerator.prototype._NumSign = function()
{
	// not implemented
}

visir.HPFunctionGenerator.prototype._SetEnteredNumber = function(scale)
{
	var num = parseInt(this._enterNumStr, 10);
	var val = this._values[this._currentValue];

	this._SetActiveValue(num * val.multiplier * scale, val.digit);
	this._SetButtonMode(this.NORMAL);
}

visir.HPFunctionGenerator.prototype._ButtonPressed = function(buttonName)
{
	if (this._enterMode == this.NORMAL) this._NormalButtonPressed(buttonName);
	else this._EnterNumButtonPressed(buttonName);

	this._UpdateDisplay();
}

visir.HPFunctionGenerator.prototype._NormalButtonPressed = function(buttonName)
{
	switch(buttonName) {
		case "sine": this.SetWaveform("sine"); this._UpdateDisplay(); break;
		case "square": this.SetWaveform("square"); this._UpdateDisplay(); break;
		case "triangle": this.SetWaveform("triangle"); this._UpdateDisplay(); break;
		case "rampup": this.SetWaveform("rampup"); this._UpdateDisplay(); break;
		
		case "freq": this.SetActiveValue("freq"); break;
		case "ampl": this.SetActiveValue("ampl"); break;
		case "offset": this.SetActiveValue("offset"); break;
		
		case "right":
			var val = this._values[this._currentValue];
			this._SetActiveValue(val.value, val.digit - 1);
			break;
		case "left":
			var val = this._values[this._currentValue];
			this._SetActiveValue(val.value, val.digit + 1);
			break;
		
		case "up": this._IncDigit(); break;
		case "down": this._DecDigit(); break;

		case "enternumber": this._SetButtonMode(this.ENTERNUM); break;

		default:
			trace("unknown button in normal mode: " + buttonName);
			break;
	}
}

visir.HPFunctionGenerator.prototype._EnterNumButtonPressed = function(buttonName)
{
	switch(buttonName) {
		case "sine":	this._AddNum("1"); break;
		case "square":	this._AddNum("2"); break;
		case "triangle":	this._AddNum("3"); break;
		case "rampup":	this._AddNum("4"); break;
		case "noise":	this._AddNum("5"); break;
		case "freq":	this._AddNum("6"); break;
		case "ampl":	this._AddNum("7"); break;
		case "offset":	this._AddNum("8"); break;
		case "single":	this._AddNum("9"); break;
		case "recall":	this._AddNum("0"); break;

		case "enternumber": this._AddNum(".");	break;

		case "left":	this._RemoveNum();	break;		
		case "arb": 	this._NumSign();		break;

		case "enter":	this._SetEnteredNumber(1);	break;
		case "up":		this._SetEnteredNumber(1000000);	break;
		case "down":	this._SetEnteredNumber(1000); break;
		case "right":	this._SetEnteredNumber(1); break;
		default:
			trace("unknown button in enter number mode: " + buttonName);
			break;		
	}
}

visir.HPFunctionGenerator.prototype._GetDisplayDigitInfo = function(realval, digits, activedigit, valunit)
{
	var unit = this._GetUnit(realval);
	realval /= Math.pow(10, unit.pow); // compensate for prefixes

	var num = numDigits(realval); // count the number of digits before .
	var display = realval.toFixed(digits - num);
	var prefixedunit = unit.unit + valunit;
	var digit = activedigit - unit.pow - num;

	return { display: display, unit: prefixedunit, digit: digit };
}

visir.HPFunctionGenerator.prototype._UpdateDisplay = function(ch)
{
	// show the selected waveform indicator
	this._$elem.find(".funcselect img").removeClass("active");
	var set = this.GetWaveform();
	switch(set) {
		case "rampup": set = "rampup"; break;
		case "rampdown": set = "rampup"; break;
	}
	this._$elem.find(".funcselect img." + set).addClass("active");

	// display the selected value
	var val = this._values[this._currentValue];
	/*
	var realval = val.value / val.multiplier;
	var unit = GetUnit(realval);
	realval /= Math.pow(10, unit.pow);
	//trace("X:" + realval + " " + numDigits(realval) + " " + val.value + " " + val.digit);

	var len = val.numDigits;
	var num = numDigits(realval);
	var digitoffset = unit.pow;
	var out = realval.toFixed(len - num);
	*/

	if (this._enterMode == this.NORMAL) {
		var info = this._GetDisplayDigitInfo(val.value / val.multiplier, val.numDigits, val.digit, val.unit);
		this._$elem.find(".num_display").html(visir.LightNum(info.display, info.digit));
		this._$elem.find(".num_unit").html(info.unit);
	} else {
		this._$elem.find(".num_display").html(this._enterNumStr);
		this._$elem.find(".num_unit").html("");
	}

	/*this._$elem.find(".num_display").html(visir.LightNum(out, val.digit - digitoffset - num));

	var unitprefix = unit.unit;
	this._$elem.find(".num_unit").html(unitprefix + val.unit);
	*/
}

visir.HPFunctionGenerator.prototype.SetActiveValue = function(val)
{
	this._currentValue = val;
	this._UpdateDisplay();
}

visir.HPFunctionGenerator.prototype._GetUnit = function(val)
{
	var units = [
		, ["M", 6 ]
		, ["K", 3 ]
		, ["", 0]
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

visir.HPFunctionGenerator.prototype._SetActiveValue = function(value, digit) {
	trace("SetActiveValue: " + value + " " + digit);
	var val = this._values[this._currentValue];
	var ok = true;
	if (value > val.max || value < val.min)	ok = false;

	trace("XXX: " + Math.pow(10, digit) + " " +  value + " " + (value / val.multiplier));

	// test if active digit is outside display range (upper bound)
	if ((Math.abs(value / val.multiplier) >= 1.0) && (Math.pow(10, digit) > Math.abs(value))) ok = false;
	// XXX: lower bounds check of digit should check if the active digit will still be visible after update

	var info = this._GetDisplayDigitInfo(value / val.multiplier, val.numDigits, digit, "");
	if (info.digit < 0) ok = false;

	if (ok) {
		val.digit = digit;
		val.value = value;

		var realvalue = val.value / val.multiplier;
		switch(this._currentValue) {
			case "freq": this._frequency = realvalue; break;
			case "ampl": this._amplitude = realvalue; break;
			case "offset": this._offset = realvalue; break;
			default:
				throw "Unknown value type";
		}
	}
	this._UpdateDisplay();
}


visir.HPFunctionGenerator.prototype._DecDigit = function() {
	var val = this._values[this._currentValue];
	var tmp = val.value - Math.pow(10, val.digit);
	this._SetActiveValue(tmp, val.digit);
}

visir.HPFunctionGenerator.prototype._IncDigit = function() {
	var val = this._values[this._currentValue];
	//val.value += Math.pow(10, val.digit);
	var tmp = val.value + Math.pow(10, val.digit);
	this._SetActiveValue(tmp, val.digit);
}
