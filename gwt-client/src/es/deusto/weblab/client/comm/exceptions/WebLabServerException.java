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
package es.deusto.weblab.client.comm.exceptions;

public class WebLabServerException extends CommException{
	private static final long serialVersionUID = -3449940969233430591L;

	public WebLabServerException() {
		super();
	}

	public WebLabServerException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

	public WebLabServerException(String arg0) {
		super(arg0);
	}

	public WebLabServerException(Throwable arg0) {
		super(arg0);
	}
}
