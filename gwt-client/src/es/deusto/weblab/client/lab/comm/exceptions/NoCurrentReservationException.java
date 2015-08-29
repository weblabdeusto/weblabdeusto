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
package es.deusto.weblab.client.lab.comm.exceptions;

import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;

public class NoCurrentReservationException extends UserProcessingException {
	private static final long serialVersionUID = -2781285087668712686L;

	public NoCurrentReservationException() {}

	public NoCurrentReservationException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

	public NoCurrentReservationException(String arg0) {
		super(arg0);
	}

	public NoCurrentReservationException(Throwable arg0) {
		super(arg0);
	}
}
