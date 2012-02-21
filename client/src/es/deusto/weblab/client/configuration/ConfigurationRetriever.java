/*
* Copyright (C) 2005 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo@ordunya.com>
* 		  Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.configuration;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;

/**
 * ConfigurationRetriever class is able to read values of different types
 * from a dictionary of JSON values. Each retriever can have one parent,
 * and values can be found on them recursively.
 */
public class ConfigurationRetriever implements IConfigurationRetriever {
	
	protected final Map<String, JSONValue> configurationMap;
	
	protected final ConfigurationRetriever parent;
	
	/**
	 * Creates a ConfigurationRetriever.
	 * @param configurationMap Map of JSON values which can be retrieved.
	 * @param parent Parant retriever that this retriever belongs to. If items
	 * are not found on this retriever's dictionary, the parents' will be checked.
	 */
	ConfigurationRetriever(Map<String, JSONValue> configurationMap, ConfigurationRetriever parent){
		this.configurationMap = configurationMap;
		this.parent = parent;
		
		basicGwtInitialization();
	}
	
	/**
	 * Constructs an empty configuration retriever, with no parent.
	 */
	public ConfigurationRetriever(){
		 this(new HashMap<String, JSONValue>(), null);
	}
	
	/**
	 * Adds certain basic GWT values to the dictionary.
	 */
	private void basicGwtInitialization(){
		this.configurationMap.put("gwt.host.page.base.url", new JSONString(GWT.getHostPageBaseURL()));
		this.configurationMap.put("gwt.module.base.url", new JSONString(GWT.getModuleBaseURL()));
		this.configurationMap.put("gwt.module.name", new JSONString(GWT.getModuleName()));
		this.configurationMap.put("gwt.version", new JSONString(GWT.getVersion()));
	}
	
	
	/**
	 * Retrieves the specified JSON property, searching for it on the
	 * parent Retriever if required. For internal use.
	 * @param key Key to search for. Parents have lower priority.
	 * @return JSON value that corresponds to the key, or null if neither 
	 * "this" retriever nor its parents contain such key.
	 */
	private JSONValue getJSONProperty(String key) {
		
		// Find the first Retriever to have the key, considering that the "this"
		// retriever is potentially the first.
		final ConfigurationRetriever owner = getPropertyFirstOwner(key);
		
		// If no retriever has the key, just return null
		if(owner == null)
			return null;
		
		// We found a retriever with the key, return that key
		return owner.configurationMap.get(key);
	}
	
	
	/**
	 * Find which is the first ConfigurationRetriever in the inverse hierarchy
	 * which has a property with the specified name. The ConfigurationRetrievers
	 * will be queried from bottom to top. That is, the first retriever queried will
	 * be the "this" retriever, and if not found, its parents will be queried in order.
	 * 
	 * @param key Name of the property whose owner to retrieve
	 * @return First ConfigurationRetriever (from "this" upwards) which contains a key
	 * with the specified name. Null if no ConfigurationRetriever in the line has
	 * such property.
	 */
	private ConfigurationRetriever getPropertyFirstOwner(String key) {
		ConfigurationRetriever retr = this;
		
		// Go through the list of retrievers upwards, until we find one which
		// has a key with the specified name
		while(retr != null && retr.configurationMap.get(key) == null ) 
			retr = retr.parent;
		
		// Return the retriever we found
		return retr;
	}

	/**
	 * Retrieves an integer property. Will throw if the property is not found
	 * after searching the retriever and its parent.
	 * @param key String which uniquely identifies the property
	 */
	@Override
	public int getIntProperty(String key) 
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException
	{
		final JSONValue value = this.getJSONProperty(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		
		final JSONNumber numberValue = value.isNumber();
		if(numberValue == null)
			throw new InvalidConfigurationValueException("Invalid number format for key " + key);
		return (int)numberValue.doubleValue();
	}
	
	
	/**
	 * Retrieves an integer property.
	 * @param key String which uniquely identifies the property
	 */
	@Override
	public int getIntProperty(String key, int def){
		final JSONValue value = this.getJSONProperty(key);
		if(value == null)
			return def;
		
		final JSONNumber numberValue = value.isNumber();
		if(numberValue == null)
			return def;
		
		return (int)numberValue.doubleValue();
	}
	
	/**
	 * Retrieves a String property. Will throw an exception if not found.
	 * @param key String which uniquely identifies the property
	 */
	@Override
	public String getProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException{
		final JSONValue value = this.getJSONProperty(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");

		final JSONString stringValue = value.isString();
		if(stringValue == null)
			throw new InvalidConfigurationValueException("Invalid string format for key " + key);
		
		return stringValue.stringValue();
	}
	
	
	/**
	 * Sets the current ConfigurationRetriever's property to the specified
	 * value. If a parent of the ConfigurationRetriever has a property
	 * with the same name, that property is not affected. 
	 * @param key Name of the property to set
	 * @param value Value to set the property to
	 */
	public void setCurrentProperty(String key, String value) {
		final JSONValue jsonVal = new JSONString(value);
		this.configurationMap.put(key, jsonVal);
	}
	
	/**
	 * Sets the current ConfigurationRetriever's property to the specified
	 * value. If a parent of the ConfigurationRetriever has a property
	 * with the same name, that property is not affected. 
	 * @param key Name of the property to set
	 * @param value Value to set the property to
	 */
	public void setCurrentIntProperty(String key, int value) {
		final JSONValue jsonVal = new JSONNumber(value);
		this.configurationMap.put(key, jsonVal);
	}
	
	/**
	 * Sets the current ConfigurationRetriever's property to the specified
	 * value. If a parent of the ConfigurationRetriever has a property
	 * with the same name, that property is not affected. 
	 * @param key Name of the property to set
	 * @param value Value to set the property to
	 */
	public void setCurrentBoolProperty(String key, boolean value) {
		final JSONValue jsonVal = JSONBoolean.getInstance(value);
		this.configurationMap.put(key, jsonVal);
	}
	
	/**
	 * Sets the specified property. It will first check whether the property exists
	 * already. It will check from the "this" retriever to its parents, upwards. If it
	 * does exist, it will be set on that retriever. If it does not exist, it will be
	 * set on the current "this" retriever.
	 * 
	 * @param key Name of the property to set
	 * @param value New value of the property
	 * 
	 * @see setCurrentProperty
	 */
	public void setProperty(String key, String value) {			
		// Find who has the property we will set
		ConfigurationRetriever owner = this.getPropertyFirstOwner(key);
		
		// Nobody has the property, we will set the property in ourselves
		if(owner == null) 
			owner = this;
		
		// Set the property.
		owner.setCurrentProperty(key, value);
	}
	
	/**
	 * Sets the specified property. It will first check whether the property exists
	 * already. It will check from the "this" retriever to its parents, upwards. If it
	 * does exist, it will be set on that retriever. If it does not exist, it will be
	 * set on the current "this" retriever.
	 * 
	 * @param key Name of the property to set
	 * @param value New value of the property
	 * 
	 * @see setCurrentProperty
	 */
	public void setIntProperty(String key, int value) {			
		// Find who has the property we will set
		ConfigurationRetriever owner = this.getPropertyFirstOwner(key);
		
		// Nobody has the property, we will set the property in ourselves
		if(owner == null) 
			owner = this;
		
		// Set the property.
		owner.setCurrentIntProperty(key, value);
	}
	
	
	/**
	 * Sets the specified property. It will first check whether the property exists
	 * already. It will check from the "this" retriever to its parents, upwards. If it
	 * does exist, it will be set on that retriever. If it does not exist, it will be
	 * set on the current "this" retriever.
	 * 
	 * @param key Name of the property to set
	 * @param value New value of the property
	 * 
	 * @see setCurrentProperty
	 */
	public void setBoolProperty(String key, boolean value) {			
		// Find who has the property we will set
		ConfigurationRetriever owner = this.getPropertyFirstOwner(key);
		
		// Nobody has the property, we will set the property in ourselves
		if(owner == null) 
			owner = this;
		
		// Set the property.
		owner.setCurrentBoolProperty(key, value);
	}
	 
	 
	/**
	 * Retrieves a string property. If the property is not found,
	 * a default value is returned.
	 * @param key String which uniquely identifies the property
	 * @param def Default string to return in case no string is found for the
	 * specified key.
	 */
	@Override
	public String getProperty(String key, String def){
		final JSONValue s = this.getJSONProperty(key);
		if(s == null)
			return def;
		
		final JSONString stringValue = s.isString();
		if(stringValue == null)
			return def;
		
		return stringValue.stringValue();
	}
	
	/**
	 * Retrieves a boolean property. Will throw a not found exception if the 
	 * property is not located.
	 * 
	 * @param key String which uniquely identifies the boolean property
	 */
	@Override
	public boolean getBoolProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException
	{
		final JSONValue value = this.getJSONProperty(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		
		final JSONBoolean booleanValue = value.isBoolean();
		if(booleanValue == null)
			throw new InvalidConfigurationValueException("Invalid boolean format for key " + key);
		
		return booleanValue.booleanValue();
	}

	/**
	 * Retrieves a boolean property. If the property is not found,
	 * a default value will be returned.
	 * 
	 * @param key String that uniquely identifies the property.
	 * @param def Value to be returned if a boolean with the specified key is not found.
	 * @return The value for the key if found, the default value otherwise.
	 */
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
