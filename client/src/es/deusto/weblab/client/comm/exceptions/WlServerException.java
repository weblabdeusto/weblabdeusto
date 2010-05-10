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
package es.deusto.weblab.client.comm.exceptions;

public class WlServerException extends WlCommException{
	private static final long serialVersionUID = -3449940969233430591L;

	public WlServerException() {
		super();
	}

	public WlServerException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

	public WlServerException(String arg0) {
		super(arg0);
	}

	public WlServerException(Throwable arg0) {
		super(arg0);
	}
}
