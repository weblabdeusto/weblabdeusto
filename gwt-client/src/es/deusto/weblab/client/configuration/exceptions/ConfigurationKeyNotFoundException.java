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
package es.deusto.weblab.client.configuration.exceptions;

public class ConfigurationKeyNotFoundException extends ConfigurationException {
	private static final long serialVersionUID = 352430998968365619L;

	public ConfigurationKeyNotFoundException() {
	}

	public ConfigurationKeyNotFoundException(String arg0) {
		super(arg0);
	}

	public ConfigurationKeyNotFoundException(Throwable arg0) {
		super(arg0);
	}

	public ConfigurationKeyNotFoundException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

}
