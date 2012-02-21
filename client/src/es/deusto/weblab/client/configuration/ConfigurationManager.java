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
import java.util.Map;

import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationException;

public class ConfigurationManager extends ConfigurationRetriever implements IConfigurationManager {

	private final String configurationPath;
	private final IConfigurationLoadedCallback callback;
		
	public ConfigurationManager(String path, IConfigurationLoadedCallback callback){
		this.configurationPath = path;
		this.callback = callback;
	}
	
	public void start(){
		final RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, this.configurationPath);
		try {
			builder.sendRequest(null, new RequestCallback(){
				@Override
				public void onError(Request request, Throwable exception) {
					ConfigurationManager.this.callback.onFailure(exception);
				}

				@Override
				public void onResponseReceived(Request request, Response response) {
					if(response.getStatusCode() / 100 == 2 || response.getStatusCode() / 100 == 3){
						final JSONValue value;
						try{
							value = JSONParser.parseLenient(response.getText());
						}catch(final Exception e){
							ConfigurationManager.this.callback.onFailure(new ConfigurationException("Error parsing configuration: " + e.getMessage(), e));
							return;
						}
						
						final JSONObject objValue = value.isObject();
						if(objValue == null){
							ConfigurationManager.this.callback.onFailure(new ConfigurationException("Error parsing configuration: object expected"));
							return;
						}
						
						for(final String key : objValue.keySet()){
							final JSONValue currentValue = objValue.get(key);
							if(currentValue == null){
								ConfigurationManager.this.callback.onFailure(new ConfigurationException("Error parsing configuration: empty value for key: " + key));
								return;
							}
							ConfigurationManager.this.configurationMap.put(key, currentValue);
						}
						
						ConfigurationManager.this.callback.onLoaded();
					}else{
						ConfigurationManager.this.callback.onFailure(new ConfigurationException("Invalid status code: " + response.getStatusCode() + "; " + response.getStatusText()));
					}
				}
			});
		} catch (final RequestException e1) {
			ConfigurationManager.this.callback.onFailure(new ConfigurationException("Exception thrown creating request: " + e1.getMessage()));
		}
	}

	@Override
	public IConfigurationRetriever [] getExperimentsConfiguration(String experimentType) throws InvalidConfigurationValueException {
		final JSONValue value = this.configurationMap.get("experiments");
		if(value == null) // If no experiment is configured, just return an empty array
			return new IConfigurationRetriever[]{};
		
		final JSONObject objectValue = value.isObject();
		if(objectValue == null)
			throw new InvalidConfigurationValueException("'experiments' field in the configuration file must be an object!!!");
		
		final JSONValue experimentTypeValue = objectValue.get(experimentType);
		if(experimentTypeValue == null) // If no experiment of that type is configured, just return an empty array
			return new IConfigurationRetriever[]{};
		
		final JSONArray experimentTypeArray = experimentTypeValue.isArray();
		if(experimentTypeArray == null)
			throw new InvalidConfigurationValueException("Any experiment type in the 'experiments' field of the configuration file must be an array!");
		
		final IConfigurationRetriever [] resultingConfigurationRetrievers = new IConfigurationRetriever[experimentTypeArray.size()];
		for(int i = 0; i < experimentTypeArray.size(); ++i){
			final JSONValue currentExperimentConfiguration = experimentTypeArray.get(i);
			final JSONObject currentExperimentConfigurationObject = currentExperimentConfiguration.isObject();
			if(currentExperimentConfigurationObject == null)
				throw new InvalidConfigurationValueException("Any experiment in the array of experiment types of 'experiments' in the configuration file must be an object!");
			
			final Map<String, JSONValue> experimentConfiguration = new HashMap<String, JSONValue>();
			for(final String key : currentExperimentConfigurationObject.keySet())
				experimentConfiguration.put(key, currentExperimentConfigurationObject.get(key));
			
			resultingConfigurationRetrievers[i] = new ConfigurationRetriever(experimentConfiguration, this);
		}
		
		return resultingConfigurationRetrievers;
	}
}
