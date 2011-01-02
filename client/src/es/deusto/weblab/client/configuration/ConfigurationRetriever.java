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

import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;

public class ConfigurationRetriever implements IConfigurationRetriever {
	
	protected final Map<String, JSONValue> configurationMap;
	
	public ConfigurationRetriever(){
		 this.configurationMap = new HashMap<String, JSONValue>();
	}
	
	ConfigurationRetriever(Map<String, JSONValue> configurationMap){
		this.configurationMap = configurationMap;
	}

	@Override
	public int getIntProperty(String key) 
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException
	{
		final JSONValue value = this.configurationMap.get(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		
		final JSONNumber numberValue = value.isNumber();
		if(numberValue == null)
			throw new InvalidConfigurationValueException("Invalid number format for key " + key);
		return (int)numberValue.doubleValue();
	}
	
	@Override
	public int getIntProperty(String key, int def){
		final JSONValue value = this.configurationMap.get(key);
		if(value == null)
			return def;
		
		final JSONNumber numberValue = value.isNumber();
		if(numberValue == null)
			return def;
		
		return (int)numberValue.doubleValue();
	}
	
	@Override
	public String getProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException{
		final JSONValue value = this.configurationMap.get(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");

		final JSONString stringValue = value.isString();
		if(stringValue == null)
			throw new InvalidConfigurationValueException("Invalid string format for key " + key);
		
		return stringValue.stringValue();
	}
	 
	@Override
	public String getProperty(String key, String def){
		final JSONValue s = this.configurationMap.get(key);
		if(s == null)
			return def;
		
		final JSONString stringValue = s.isString();
		if(stringValue == null)
			return def;
		
		return stringValue.stringValue();
	}
	
	@Override
	public boolean getBoolProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException
	{
		final JSONValue value = this.configurationMap.get(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		
		final JSONBoolean booleanValue = value.isBoolean();
		if(booleanValue == null)
			throw new InvalidConfigurationValueException("Invalid boolean format for key " + key);
		
		return booleanValue.booleanValue();
	}

	@Override
	public boolean getBoolProperty(String key, boolean def)
	{
		final JSONValue value = this.configurationMap.get(key);
		if(value == null)
			return def;
		
		final JSONBoolean booleanValue = value.isBoolean();
		if(booleanValue == null)
			return def;
		
		return booleanValue.booleanValue();
	}
}
