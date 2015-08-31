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

import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.ExperimentParameterDefault;

/**
 * Retrieve configuration arguments. 
 */
public interface IConfigurationRetriever {

	/**
	 * Retrieve an integer configuration argument
	 * 
	 * @param key Name of the argument
	 * @return Value of the configuration argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public int getIntProperty(String key)
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	/**
	 * Retrieve an integer configuration argument, without a default value
	 * 
	 * @param key Name of the argument
	 * @param def Default argument if the key is not present or it is present with a wrong value (not int)
	 * @return Value of the configuration argument
	 */
	public int getIntProperty(String key, int def);

	/**
	 * Retrieve an integer configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public int getIntProperty(ExperimentParameter parameter) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	/**
	 * Retrieve an integer configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public int getIntProperty(ExperimentParameterDefault parameter);


	/**
	 * Retrieve a boolean configuration argument
	 * 
	 * @param key Name of the argument
	 * @return Value of the configuration argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not a boolean.
	 */
	public boolean getBoolProperty(String key)
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	
	/**
	 * Retrieve a boolean configuration argument, passing a default value
	 * 
	 * @param key Name of the argument
	 * @param def Default argument if the key is not present or it is present with a wrong value (not boolean)
	 * @return Value of the configuration argument
	 */
	public boolean getBoolProperty(String key, boolean def);


	/**
	 * Retrieve an boolean configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public boolean getBoolProperty(ExperimentParameter parameter) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	/**
	 * Retrieve an boolean configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public boolean getBoolProperty(ExperimentParameterDefault parameter);

	
	/**
	 * Retrieve a string configuration argument
	 * 
	 * @param key Name of the argument
	 * @return Value of the configuration argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an string.
	 */
	public String getProperty(String key)
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	
	/**
	 * Retrieve a string configuration argument, passing a default value
	 * 
	 * @param key Name of the argument
	 * @param def Default argument if the key is not present or it is present with a wrong value (not string)
	 * @return Value of the configuration argument
	 */
	public String getProperty(String key, String def);
	
	/**
	 * Retrieve an string configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public String getProperty(ExperimentParameter parameter) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	/**
	 * Retrieve an string configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public String getProperty(ExperimentParameterDefault parameter);
	
	/**
	 * Retrieve an integer configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public double getDoubleProperty(ExperimentParameter parameter) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	/**
	 * Retrieve an float configuration argument
	 * 
	 * @param parameter Name of the argument
	 * @throws ConfigurationKeyNotFoundException The key is not present
	 * @throws InvalidConfigurationValueException The key is present, but it is not an int.
	 */
	public double getDoubleProperty(ExperimentParameterDefault parameter);

}
