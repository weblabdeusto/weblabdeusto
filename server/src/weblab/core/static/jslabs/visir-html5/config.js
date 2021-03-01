var visir = visir || {};

visir.ConfigClass = function()
{
	this._teacherMode = true;
	this._instrReg = null;
	this._manualInstConfig = null;
	this._readOnly = false;
	this._dcPower25 = true;
	this._dcPowerM25 = true;
	this._dcPower6 = true;
	this._unrFormat = false; // Support Universidad Nacional de Rosario format
	this._libraryXml = null;
	this._maxOscMeasureCount = 10;
	this._displayManuals = true;
	this._cacheBuster = null;
	this._vppInFuncgen = true;
	this._disableLoadSave = true;

	var base = "";
	if (visir.BaseLocation) base = visir.BaseLocation;
}

visir.ConfigClass.prototype.GetDeferredConfigLoader = function(configUrlOrObject)
{
	var me = this;

	var def = $.Deferred();

	if (typeof(configUrlOrObject) === 'object') {
		me.ReadConfig(configUrlOrObject);
		def.resolve();
	} else {
		var url = configUrlOrObject;
		if (!url.endsWith(".json")) {
			url = url + "config.json";
		}
		$.get(url, function(data) {
			me.ReadConfig(data);
		}, "json")
		.error( function(obj, msg) {
			alert("failed to read config.json. " + msg);
		}).always( function() {
			def.resolve();
		});
	}
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
	this._libraryXml = (config.libraryXml !== undefined)?config.libraryXml:null;
	this._maxOscMeasureCount = (config.maxOscMeasureCount !== undefined)?config.maxOscMeasureCount:10;
	this._dcPower25 = (config.dcPower25 !== undefined)?config.dcPower25:true;
	this._dcPowerM25 = (config.dcPowerM25 !== undefined)?config.dcPowerM25:true;
	this._dcPower6 = (config.dcPower6 !== undefined)?config.dcPower6:true;
	this._displayManuals = (config.displayManuals !== undefined)?config.displayManuals:true;
	this._cacheBuster = (config.cacheBuster !== undefined)?config.cacheBuster:null;
	this._unrFormat = (config.unrFormat !== undefined)?config.unrFormat:false;
	this._vppInFuncgen = (config.vppInFuncgen !== undefined)?config.vppInFuncgen:true;
	this._disableLoadSave = (config.disableLoadSave !== undefined)?config.disableLoadSave:false;
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
		case "maxOscMeasureCount": return this._maxOscMeasureCount;
		case "libraryXml": return this._libraryXml;
		case "dcPower25": return this._dcPower25;
		case "dcPowerM25": return this._dcPowerM25;
		case "dcPower6": return this._dcPower6;
		case "displayManuals": return this._displayManuals;
		case "cacheBuster": return this._cacheBuster;
		case "unrFormat": return this._unrFormat;
		case "vppInFuncgen": return this._vppInFuncgen;
		case "disableLoadSave": return this._disableLoadSave;
	}

	return undefined;
}

visir.ConfigClass.prototype.Set = function(name, value)
{
	switch(name) {
		case "teacher": 
			this._teacherMode = value;
			break;
		case "locale": 
			this._locale = value;
			break;
		case "mesServer": 
			this._mesServer = value;
			break;
		case "readOnly": 
			this._readOnly = value;
			break;
		case "transMethod": 
			this._transMethod = value;
			break;
		case "oscRunnable": 
			this._oscRunnable = value;
			break;
		case "maxOscMeasureCount": 
			this._maxOscMeasureCount = value;
			break;
		case "libraryXml": 
			this._libraryXml = value;
			break;
		case "dcPower25": 
			this._dcPower25 = value;
			break;
		case "dcPowerM25": 
			this._dcPowerM25 = value;
			break;
		case "dcPower6": 
			this._dcPower6 = value;
			break;
		case "displayManuals": 
			this._displayManuals = value;
			break;
		case "cacheBuster": 
			this._cacheBuster = value;
			break;
		case "unrFormat": 
			this._unrFormat = value;
			break;
		case "vppInFuncgen":
			this._vppInFuncgen = value;
			break;
		case "disableLoadSave":
			this._disableLoadSave = value;
			break;

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
