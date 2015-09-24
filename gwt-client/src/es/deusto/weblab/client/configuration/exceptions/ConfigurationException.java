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

import es.deusto.weblab.client.WebLabException;

public class ConfigurationException extends WebLabException {
	private static final long serialVersionUID = 6775556180372843714L;

	public ConfigurationException() {
	}

	public ConfigurationException(String arg0) {
		super(arg0);
	}

	public ConfigurationException(Throwable arg0) {
		super(arg0);
	}

	public ConfigurationException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

}
