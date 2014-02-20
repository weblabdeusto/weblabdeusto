var visir = visir || {};

visir.ConfigClass = function()
{
	this._teacherMode = true;
	this._instrReg = null;
	this._manualInstConfig = null;

	var base = "";
	if (visir.BaseLocation) base = visir.BaseLocation;
}

visir.ConfigClass.prototype.GetDeferredConfigLoader = function(baseurl)
{
	var me = this;

	var def = $.Deferred();

	$.get(baseurl + "config.json", function(data) {
		me.ReadConfig(data);
	}, "json")
	.error( function(obj, msg) {
		alert("failed to read config.json. " + msg);
	}).always( function() {
		def.resolve();
	});

	return def;
}

visir.ConfigClass.prototype.ReadConfig = function(config)
{
	this._teacherMode = config.teacherMode;
	this._instrReg = config.instrReg;
	this._locale = config.locale;
	this._mesServer = config.mesServer;
	this._readOnly = config.readOnly;
	this._transMethod = config.transMethod;
	this._oscRunnable = config.oscRunnable;
}

visir.ConfigClass.prototype.Get = function(name)
{
	switch(name) {
		case "teacher": return this._teacherMode;
		case "locale": return this._locale;
		case "mesServer": return this._mesServer;
		case "readOnly": return this._readOnly;
		case "transMethod": return this._transMethod;
		case "oscRunnable": return this._oscRunnable;
	}

	return undefined;
}

visir.ConfigClass.prototype.Set = function(name, value)
{
	switch(name) {
		case "teacher": this._teacherMode = value;
		case "locale": this._locale = value;
		case "mesServer": this._mesServer = value;
		case "readOnly": this._readOnly = value;
		case "transMethod": this._transMethod = value;
		case "oscRunnable": this._oscRunnable = value;
	}
}

visir.ConfigClass.prototype.SetInstrRegistry = function(registry)
{
	this._instrReg = registry;
}

visir.ConfigClass.prototype.SetManualInstrConfig = function(instrmap)
{
	this._manualInstConfig = instrmap;
}

visir.ConfigClass.prototype.GetNrInstrOfType = function(type)
{
	if (this._manualInstConfig) return this._manualInstConfig[type];
	if (this._instrReg) return this._instrReg.GetNrInstrOfType(type);
	return 1;
}

visir.Config = new visir.ConfigClass();