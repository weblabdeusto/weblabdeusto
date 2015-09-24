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

public class InvalidConfigurationValueException extends
		ConfigurationException {
	private static final long serialVersionUID = -6988193670495700702L;

	public InvalidConfigurationValueException() {
	}

	public InvalidConfigurationValueException(String arg0) {
		super(arg0);
	}

	public InvalidConfigurationValueException(Throwable arg0) {
		super(arg0);
	}

	public InvalidConfigurationValueException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

}
