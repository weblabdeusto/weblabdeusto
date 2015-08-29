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
package es.deusto.weblab.client.lab.controller.exceptions.status;

public class IllegalStateFoundException extends ControllerStateException {
	private static final long serialVersionUID = 1L;

	public IllegalStateFoundException() {
	}

	public IllegalStateFoundException(String arg0) {
		super(arg0);
	}

	public IllegalStateFoundException(Throwable arg0) {
		super(arg0);
	}

	public IllegalStateFoundException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}
}
