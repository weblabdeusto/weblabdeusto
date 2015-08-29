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
package es.deusto.weblab.client.ui.exceptions;

import es.deusto.weblab.client.WebLabException;

public class UIException extends WebLabException {
	private static final long serialVersionUID = -5011397264280350488L;

	public UIException() {
		super();
	}

	public UIException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

	public UIException(String arg0) {
		super(arg0);
	}

	public UIException(Throwable arg0) {
		super(arg0);
	}
}
