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
package es.deusto.weblab.client.exceptions.controller;

import es.deusto.weblab.client.exceptions.WlClientException;

public class WlControllerException extends WlClientException {
	private static final long serialVersionUID = 8564258070075299803L;

	public WlControllerException() {}

	public WlControllerException(String arg0) {
		super(arg0);
	}

	public WlControllerException(Throwable arg0) {
		super(arg0);
	}

	public WlControllerException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}
}
