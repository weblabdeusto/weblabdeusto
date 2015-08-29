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
package es.deusto.weblab.client;

public class WebLabException extends Exception {
	private static final long serialVersionUID = 2121509209824799580L;

	public WebLabException() {
	}

	public WebLabException(String arg0) {
		super(arg0);
	}

	public WebLabException(Throwable arg0) {
		super(arg0);
	}

	public WebLabException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

}
