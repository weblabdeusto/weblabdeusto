var visir = visir || {};

visir.Load = function( onSuccess, onFailure, baseurl, configUrlOrObject )
{
	baseurl = baseurl || "";
	visir.BaseLocation = baseurl;
    if (!configUrlOrObject) 
        configUrlOrObject = baseurl + "config.json";

    // Always an object, so applied immediately
    visir.Config.GetDeferredConfigLoader(configUrlOrObject);

    onSuccess();
}

