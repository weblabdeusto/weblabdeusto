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
package es.deusto.weblab.client.comm.exceptions.user_processing;

import es.deusto.weblab.client.comm.exceptions.WlServerException;

public class SessionNotFoundException extends WlServerException {
	private static final long serialVersionUID = -6226878120339049068L;

	public SessionNotFoundException() {}

	public SessionNotFoundException(String arg0) {
		super(arg0);
	}

	public SessionNotFoundException(Throwable arg0) {
		super(arg0);
	}

	public SessionNotFoundException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}
}
