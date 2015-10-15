var visir = visir || {};

/* XXX: this might be removed and replaced with a better interface, look out for changes */

visir.ExtServices = function(props)
{
	var options = $.extend({
		MakeMeasurement: function() {}
	}, props || {});

	this._options = options;
	this._listeners = [];
}

visir.ExtServices.prototype.MakeMeasurement = function()
{
	trace("ExtServices::MakeMeasurement");
	this._options.MakeMeasurement();
}
