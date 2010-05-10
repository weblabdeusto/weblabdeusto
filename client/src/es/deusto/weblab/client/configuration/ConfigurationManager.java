/*
* Copyright (C) 2005-2009 University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.configuration;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.configuration.exceptions.WlConfigurationException;

public class ConfigurationManager implements IConfigurationManager {

	private final String configurationPath;
	private final Map<String, String> configurationMap = new HashMap<String, String>();
	private final IConfigurationLoadedCallback callback;
		
	public ConfigurationManager(String path, IConfigurationLoadedCallback callback){
		this.configurationPath = path;
		this.callback = callback;
	}
	
	public void start(){
		final RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, this.configurationPath);
		try {
			builder.sendRequest(null, new RequestCallback(){
				public void onError(Request request, Throwable exception) {
					ConfigurationManager.this.callback.onFailure(exception);
				}

				public void onResponseReceived(Request request, Response response) {
					if(response.getStatusCode() / 100 == 2 || response.getStatusCode() / 100 == 3){
						final JSONValue value;
						try{
							value = JSONParser.parse(response.getText());
						}catch(Exception e){
							ConfigurationManager.this.callback.onFailure(new WlConfigurationException("Error parsing configuration: " + e.getMessage(), e));
							return;
						}
						
						final JSONObject objValue = value.isObject();
						if(objValue == null){
							ConfigurationManager.this.callback.onFailure(new WlConfigurationException("Error parsing configuration: object expected"));
							return;
						}
						
						for(String key : objValue.keySet()){
							final JSONValue currentValue = objValue.get(key);
							if(currentValue == null){
								ConfigurationManager.this.callback.onFailure(new WlConfigurationException("Error parsing configuration: empty value for key: " + key));
								return;
							}
							final JSONString valueString = currentValue.isString();
							if(valueString == null){
								ConfigurationManager.this.callback.onFailure(new WlConfigurationException("Error parsing configuration: string expected for key: " + key));
								return;
							}
							ConfigurationManager.this.configurationMap.put(key, valueString.stringValue());
						}
						
						ConfigurationManager.this.callback.onLoaded();
					}else{
						ConfigurationManager.this.callback.onFailure(new WlConfigurationException("Invalid status code: " + response.getStatusCode() + "; " + response.getStatusText()));
					}
				}
			});
		} catch (final RequestException e1) {
			ConfigurationManager.this.callback.onFailure(new WlConfigurationException("Exception thrown creating request: " + e1.getMessage()));
		}
	}

	public int getIntProperty(String key) 
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException
	{
		final String value = this.configurationMap.get(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		else
			try{
				return Integer.parseInt(value);
			}catch(final NumberFormatException exc){
				throw new InvalidConfigurationValueException("Invalid number format exception caught: " + exc.getMessage());
			}
	}
	
	public int getIntProperty(String key, int def){
		final String value = this.configurationMap.get(key);
		if(value == null)
			return def;
		else
			try{
				return Integer.parseInt(value);
			}catch(final NumberFormatException exc){
				return def;
			}
	}
	
	public String getProperty(String key) throws ConfigurationKeyNotFoundException{
		final String s = this.configurationMap.get(key);
		if(s == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		else
			return s;
	}
	 
	public String getProperty(String key, String def){
		final String s = this.configurationMap.get(key);
		if(s == null)
			return def;
		else
			return s;
	}
	
	public boolean getBoolProperty(String key) throws ConfigurationKeyNotFoundException
	{
		final String value = this.configurationMap.get(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		else
			return value.equals("true");
	}

	public boolean getBoolProperty(String key, boolean def)
	{
		final String value = this.configurationMap.get(key);
		if(value == null)
			return def;
		else
			return value.equals("true");
	}
}
