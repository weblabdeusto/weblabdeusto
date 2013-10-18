var visir = visir || {};

visir.Language = function()
{
	var locale = visir.Config.Get('locale');

	if ($.inArray(locale, ["en_UK", "es_ES"]) === -1)
	{
		locale = "en_UK";
	}

	strings = {};

	$.ajax({
		async: false,
		dataType: "json",
		url: '_locales/'+locale+'/messages.json'
	}).done(function(data)
	{
		strings = data;
	});

	this._strings = strings;
}

visir.Language.prototype.GetMessage = function(key)
{
	return this._strings[key].message;
}

visir.Language.prototype.GetDescription = function(key)
{
	return this._strings[key].description;
}

visir.Lang = new visir.Language();