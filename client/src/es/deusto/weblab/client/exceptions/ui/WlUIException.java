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
package es.deusto.weblab.client.exceptions.ui;

import es.deusto.weblab.client.exceptions.WlClientException;

public class WlUIException extends WlClientException {
	private static final long serialVersionUID = -5011397264280350488L;

	public WlUIException() {
		super();
	}

	public WlUIException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

	public WlUIException(String arg0) {
		super(arg0);
	}

	public WlUIException(Throwable arg0) {
		super(arg0);
	}
}
