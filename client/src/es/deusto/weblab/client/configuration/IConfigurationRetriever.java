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

import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;

public interface IConfigurationRetriever {

	public int getIntProperty(String key)
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	public int getIntProperty(String key, int def);

	public boolean getBoolProperty(String key)
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	public boolean getBoolProperty(String key, boolean def);
	
	public String getProperty(String key)
		throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException;

	public String getProperty(String key, String def);

}
