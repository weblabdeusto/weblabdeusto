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
package es.deusto.weblab.client.exceptions.configuration;

import es.deusto.weblab.client.exceptions.WlClientException;

public class WlConfigurationException extends WlClientException {
	private static final long serialVersionUID = 6775556180372843714L;

	public WlConfigurationException() {
	}

	public WlConfigurationException(String arg0) {
		super(arg0);
	}

	public WlConfigurationException(Throwable arg0) {
		super(arg0);
	}

	public WlConfigurationException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

}
