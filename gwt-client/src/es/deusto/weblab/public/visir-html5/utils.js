var visir = visir || {};

function extend(Child, Parent) {
  Child.prototype = inherit(Parent.prototype)
  Child.prototype.constructor = Child
  Child.parent = Parent.prototype
}

function inherit(proto) {
  function F() {}
  F.prototype = proto
  return new F
}

function trace(msg)
{
	$("#logwindow").append(msg + "<br/>");
	if (window.console && console.log) console.log(msg);
}

function setRotation(elem, deg)
{
	var rotateCSS = 'rotate(' + deg + 'deg)';
	elem.css({
		'transform': rotateCSS
		,'-moz-transform': rotateCSS
		,'-webkit-transform': rotateCSS
	});
}

function AddXMLValue(where, name, value) {
	where.append('<' + name + ' value="'+ value + '"/>');
}

visir.LightNum = function(strnum, digit) {
	var out = "";
	
	var idx = 0;
	for(var i=strnum.length - 1; i >= 0; i--)
	{
		if (strnum[i] == "." || strnum[i] == "-") {
			out = strnum[i] + out;
			continue;
		}
		
		if (idx == digit) {
			out = '<span class="green">'+ strnum[i] + '</span>' + out;
		} else {
			out = strnum[i] + out;
		}
		idx++;
	}
	
	return out;
}

function base64_decode(data) {
  var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
  var o1, o2, o3, h1, h2, h3, h4, bits, i = 0,
    ac = 0,
    dec = "",
    tmp_arr = [];

  if (!data) {
    return data;
  }

	data = data.replace(/[^A-Za-z0-9\+\/\=]/g, "");

  do {
    h1 = b64.indexOf(data.charAt(i++));
    h2 = b64.indexOf(data.charAt(i++));
    h3 = b64.indexOf(data.charAt(i++));
    h4 = b64.indexOf(data.charAt(i++));

    bits = h1 << 18 | h2 << 12 | h3 << 6 | h4;

    o1 = bits >> 16 & 0xff;
    o2 = bits >> 8 & 0xff;
    o3 = bits & 0xff;

		tmp_arr[ac++] = o1;
		if (h3 != 64) tmp_arr[ac++] = o2;
		if (h4 != 64) tmp_arr[ac++] = o3;
  } while (i < data.length);

  return tmp_arr;
}

visir.GetUnit = function(val)
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
