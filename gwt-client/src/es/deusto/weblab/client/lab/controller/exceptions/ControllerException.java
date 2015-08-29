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
package es.deusto.weblab.client.lab.controller.exceptions;

import es.deusto.weblab.client.WebLabException;

public class ControllerException extends WebLabException {
	private static final long serialVersionUID = 8564258070075299803L;

	public ControllerException() {}

	public ControllerException(String arg0) {
		super(arg0);
	}

	public ControllerException(Throwable arg0) {
		super(arg0);
	}

	public ControllerException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}
}
