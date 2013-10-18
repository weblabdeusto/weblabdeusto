var visir = visir || {};

visir.InstrumentRegistry = function(extService)
{
	this._instruments = [];
	this._registeredTypes = {
		circuit: 0,
		dcpower: 0,
		functiongenerator: 0,
		multimeter: 0,
		oscilloscope: 0
	};
	this._listeners = [];

	function InstrInfo(type, name, swf) { return { type: type, displayname: name, swf: swf } };
	this._instrumentInfo = {
		AgilentOscilloscope: InstrInfo("oscilloscope", visir.Lang.GetMessage("oscilloscope"), "oscilloscope/oscilloscope.swf")
		, Breadboard: InstrInfo("circuit", visir.Lang.GetMessage("breadboard"), "breadboard/breadboard.swf")
		, FlukeMultimeter: InstrInfo("multimeter", visir.Lang.GetMessage("multimeter"), "multimeter/multimeter.swf")
		, HPFunctionGenerator: InstrInfo("functiongenerator", visir.Lang.GetMessage("func_gen"), "functiongenerator/functiongenerator.swf")
		, NationalInstrumentOscilloscope: InstrInfo("oscilloscope", visir.Lang.GetMessage("oscilloscope"), "")
		, TripleDC: InstrInfo("dcpower", visir.Lang.GetMessage("dc_power"), "tripledc/tripledc.swf")
	}

	this._extServices = extService || null;

	if (visir.Config) visir.Config.SetInstrRegistry(this); // XXX: maybe this need to be more configurable..
}

visir.InstrumentRegistry.prototype._Reset = function()
{
	this._instruments = [];
	this._registeredTypes = {
		circuit: 0,
		dcpower: 0,
		functiongenerator: 0,
		multimeter: 0,
		oscilloscope: 0
	};
}

visir.InstrumentRegistry.prototype.CreateInstrument = function()
{
	function construct(constructor, args) {
		function F() {
			return constructor.apply(this, args);
		}
		F.prototype = constructor.prototype;
		return new F();
	}

	if (arguments.length < 2) throw "Invalid number of arguments to CreateInstrument";
	var name = arguments[0];
	var id = this._NextInstrID(name);
	arguments[0] = id; // replace the first argument with the id before passing them along.
	arguments[1] = $(arguments[1]); // get the jquery dom node
	var newinstr = construct(visir[name], arguments);

	var entry = { instrument: newinstr, id: id, domnode: arguments[1], instrInfo: this._instrumentInfo[name], name: name };
	this._instruments.push(entry);

	if (this._extServices && typeof newinstr.UseExteralService == "function") {
		newinstr.UseExteralService(this._extServices);
	}

	return newinstr;
}

visir.InstrumentRegistry.prototype._NextInstrID = function(name)
{
	//XXX: check the db for instr type and update the counts
	if (!this._instrumentInfo[name]) throw "Instrument name not found in InstrumentRegistry";
	return ++this._registeredTypes[this._instrumentInfo[name].type];
}

visir.InstrumentRegistry.prototype.WriteRequest = function()
{
	var out = "";
	for(var i=0;i<this._instruments.length; i++) {
		out += this._instruments[i].instrument.WriteRequest();
	}
	return out;
}

visir.InstrumentRegistry.prototype.ReadResponse = function(response)
{
	for(var i=0;i<this._instruments.length; i++) {
		this._instruments[i].instrument.ReadResponse(response);
	}
}

visir.InstrumentRegistry.prototype.ReadSave = function(response)
{
	for(var i=0;i<this._instruments.length; i++) {
		if (typeof (this._instruments[i].instrument.ReadSave) == "function") {
			this._instruments[i].instrument.ReadSave(response);
		}
	}
}

visir.InstrumentRegistry.prototype.WriteSave = function()
{
	$xml = $('<save version="2" />');
	var instrumentlist = "";
	for(var i=0;i<this._instruments.length; i++) {
		if (i>0) instrumentlist += "|";
		instrumentlist += this._instruments[i].name;
	}
	var $instruments = $('<instruments />').attr("htmlinstruments", instrumentlist);
	$xml.append($instruments);
	for(var i=0;i<this._instruments.length; i++) {
		if (typeof (this._instruments[i].instrument.WriteSave) == "function") {
			$xml.append(this._instruments[i].instrument.WriteSave());
		}
	}
	return $("<root />").append($xml).html();
}

visir.InstrumentRegistry.prototype.MakeRequest = function(transport)
{
	var me = this;
	transport.Request(this.WriteRequest(), function(res) { me.ReadResponse(res); } );
}

// XXX: don't know if this is going to stay here or in some other class
//

visir.InstrumentRegistry.prototype._CreateInstrContainer = function(type)
{
	var id = this._registeredTypes[type]+1;
	return $('<div class="instrument" id="' + type + id + '" />');
}

visir.InstrumentRegistry.prototype._CreateInstrFromSWF = function(swf, $loc)
{
	for (var key in this._instrumentInfo) {
		if (this._instrumentInfo[key].swf == swf) {
			var $ctnr = this._CreateInstrContainer(this._instrumentInfo[key].type);
			var newinstr = this.CreateInstrument(key, $ctnr);
			$loc.append($ctnr);
			return newinstr;
		}
	}
	return null;
}

visir.InstrumentRegistry.prototype.LoadExperimentFromURL = function(url, $loc)
{
	var me = this;
	$.get(url, function(data) {
		me.LoadExperiment(data, $loc);
	});
}

visir.InstrumentRegistry.prototype.CreateInstrFromJSClass = function(classname, $loc)
{
	trace("creating instrument from js name: " + classname);
	var $ctnr = this._CreateInstrContainer(this._instrumentInfo[classname].type);
	this.CreateInstrument(classname, $ctnr);
	$loc.append($ctnr);
}

visir.InstrumentRegistry.prototype.LoadExperiment = function(xmldata, $loc)
{
	$loc.find(".instrument").remove();
	this._Reset();
	var $xml = $(xmldata);
	var $instr = $xml.find("instruments");

	var flashlocs = $instr.attr("list");
	var swfs = flashlocs ? flashlocs.split("|") : [];

	for(var i=0;i<swfs.length; i++) {
		trace("creating instrument from swf: " + swfs[i]);
		this._CreateInstrFromSWF(swfs[i], $loc);
	}

	var htmlinstr = $instr.attr("htmlinstruments");
	var htmlarr = htmlinstr ? htmlinstr.split("|") : [];
	for(var i=0;i<htmlarr.length; i++) {
		this.CreateInstrFromJSClass(htmlarr[i], $loc);
	}

	this.ReadSave($xml);
	this.Notify("onExperimentLoaded");
	$("body").trigger("configChanged");
}

visir.InstrumentRegistry.prototype.AddListener = function(listenTo)
{
	this._listeners.push(listenTo);
}

// XXX: do we need to fix arguments? lets see..
visir.InstrumentRegistry.prototype.Notify = function(func)
{
	for(var i=0;i<this._listeners.length; i++) {
		if (typeof this._listeners[i][func] == "function") this._listeners[i][func]();
	}
}

visir.InstrumentRegistry.prototype.RemoveInstrument = function(instrument)
{
	for(var i in this._instruments) {
		if (this._instruments[i] === instrument) {
			// XXX: what should we do with the registeredTypes? This is not really correct
			--this._registeredTypes[this._instrumentInfo[this._instruments[i].name].type];
			this._instruments[i].domnode.remove();
			this._instruments.splice(i, 1);
		}
	}
}

visir.InstrumentRegistry.prototype.GetNrInstrOfType = function(type)
{
	trace("reg: " + this._registeredTypes[type] + " " + type);
	return this._registeredTypes[type];
}
