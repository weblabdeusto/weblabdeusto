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

/**
 * Retrieve configuration arguments. See {@link ConfigurationManager} to see where it is
 * retrieved from (a JSON file).
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
	 * Retrieve an integer configuration argument, passing a default value
	 * 
	 * @param key Name of the argument
	 * @param def Default argument if the key is not present or it is present with a wrong value (not int)
	 * @return Value of the configuration argument
	 */
	public int getIntProperty(String key, int def);

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
	
}
