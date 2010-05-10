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
package es.deusto.weblab.client.lab.ui.exceptions.themes;

import es.deusto.weblab.client.lab.ui.exceptions.WlUIException;

public class WlThemeException extends WlUIException {
	private static final long serialVersionUID = -1527186553163231260L;

	public WlThemeException() {
	}

	public WlThemeException(String arg0) {
		super(arg0);
	}

	public WlThemeException(Throwable arg0) {
		super(arg0);
	}

	public WlThemeException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

}
