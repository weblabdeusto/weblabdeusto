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
*
*/ 
package es.deusto.weblab.client.configuration;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;

public class FakeConfiguration implements IConfigurationManager {

	Map<String, String> map;
	Map<String, List<Map<String, String>>> experiments = new HashMap<String, List<Map<String, String>>>();
	
	public FakeConfiguration(Map<String, String> map){
		this.map = map;
	}
	
	public FakeConfiguration(Map<String, String> map, Map<String, List<Map<String, String>>> experiments){
		this.map = map;
		this.experiments = experiments;
	}
	
	@Override
	public int getIntProperty(String key)
			throws ConfigurationKeyNotFoundException,
			InvalidConfigurationValueException {
		final String value = this.map.get(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		else
			try{
				return Integer.parseInt(value);
			}catch(final NumberFormatException exc){
				throw new InvalidConfigurationValueException("Invalid number format exception caught: " + exc.getMessage());
			}
	}

	@Override
	public int getIntProperty(String key, int def) {
		final String value = this.map.get(key);
		if(value == null)
			return def;
		else
			try{
				return Integer.parseInt(value);
			}catch(final NumberFormatException exc){
				return def;
			}
	}

	@Override
	public String getProperty(String key)
			throws ConfigurationKeyNotFoundException {
		final String s = this.map.get(key);
		if(s == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		else
			return s;
	}

	@Override
	public String getProperty(String key, String def) {
		final String s = this.map.get(key);
		if(s == null)
			return def;
		else
			return s;
	}

	@Override
	public boolean getBoolProperty(String key)
			throws ConfigurationKeyNotFoundException {
		final String value = this.map.get(key);
		if(value == null)
			throw new ConfigurationKeyNotFoundException("Configuration key: " + key + " not found");
		else
			return value.equals("true");
	}

	@Override
	public boolean getBoolProperty(String key, boolean def) {
		final String value = this.map.get(key);
		if(value == null)
			return def;
		else
			return value.equals("true");
	}

	@Override
	public IConfigurationRetriever[] getExperimentsConfiguration(
			String experimentType) throws InvalidConfigurationValueException {
		final List<Map<String, String>> localMaps = this.experiments.get(experimentType);
		if(localMaps == null)
			return new IConfigurationRetriever[]{};
		
		final IConfigurationRetriever [] retrievers = new IConfigurationRetriever[localMaps.size()];
		
		for(int i = 0; i < retrievers.length; ++i){
			final Map<String,String> localMap = localMaps.get(i);
			retrievers[i] = new FakeConfiguration(localMap);
		}
		return retrievers;
	}
}
